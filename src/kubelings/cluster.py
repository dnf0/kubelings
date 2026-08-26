"""Kubernetes Cluster Detection and Ephemeral Test Environment Adapter."""

from typing import Any, Dict, Optional
import uuid


class ClusterDetector:
    """Detects active Kubernetes cluster contexts and manages ephemeral test namespaces."""

    def __init__(self) -> None:
        self._cached_status: Optional[Dict[str, Any]] = None

    def get_cluster_status(self, refresh: bool = False) -> Dict[str, Any]:
        """Detect and return the active Kubernetes cluster status.

        Args:
            refresh: If True, bypass the cached status and re-query Kubernetes config.

        Returns:
            Dictionary containing 'available' (bool), 'context' (str), and 'provider' (str).
        """
        if self._cached_status is not None and not refresh:
            return self._cached_status

        try:
            from kubernetes import config

            contexts, active = config.list_kube_config_contexts()
            if active and active.get("name"):
                active_name = active["name"]
                local_indicators = [
                    "kind",
                    "minikube",
                    "k3d",
                    "k3s",
                    "docker-desktop",
                    "orbstack",
                    "microk8s",
                    "colima",
                    "lima",
                ]
                is_local = any(indicator in active_name.lower() for indicator in local_indicators)
                self._cached_status = {
                    "available": True,
                    "context": active_name,
                    "provider": "local" if is_local else "cloud",
                }
            else:
                self._cached_status = {"available": False, "context": "none", "provider": "none"}
        except Exception:
            self._cached_status = {"available": False, "context": "none", "provider": "none"}

        return self._cached_status

    def is_cluster_available(self) -> bool:
        """Check if a Kubernetes cluster context is actively available."""
        return bool(self.get_cluster_status().get("available", False))

    def get_active_context(self) -> Optional[str]:
        """Return the active kubeconfig context name, or None if unavailable."""
        status = self.get_cluster_status()
        if status.get("available") and status.get("context") != "none":
            return status["context"]
        return None

    def create_ephemeral_namespace(self, prefix: str = "kubelings-test") -> Optional[str]:
        """Create an ephemeral namespace for isolated testing.

        Args:
            prefix: Name prefix for the temporary namespace.

        Returns:
            The created namespace name, or None if creation failed.
        """
        if not self.is_cluster_available():
            return None

        try:
            from kubernetes import client, config

            config.load_kube_config()
            v1 = client.CoreV1Api()

            ns_name = f"{prefix}-{uuid.uuid4().hex[:8]}"
            body = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=ns_name,
                    labels={
                        "app.kubernetes.io/managed-by": "kubelings",
                        "kubelings.dev/ephemeral": "true",
                    },
                )
            )
            v1.create_namespace(body=body)
            return ns_name
        except Exception:
            return None

    def cleanup_namespace(self, namespace: str) -> bool:
        """Clean up an ephemeral test namespace.

        Args:
            namespace: Name of the namespace to delete.

        Returns:
            True if deletion was successfully initiated, False otherwise.
        """
        if not self.is_cluster_available() or not namespace:
            return False

        try:
            from kubernetes import client, config

            config.load_kube_config()
            v1 = client.CoreV1Api()
            v1.delete_namespace(name=namespace)
            return True
        except Exception:
            return False
