"""Kubernetes Cluster Detection and Ephemeral Test Environment Adapter."""

import re
from typing import Any, Dict, Optional, Set
import uuid

# Ephemeral namespace prefix and regex pattern for safety
DEFAULT_EPHEMERAL_PREFIX = "kubelings-test"
EPHEMERAL_NAMESPACE_PATTERN = re.compile(r"^kubelings-[a-z0-9-]+\Z")

LOCAL_PROVIDER_REGEX = re.compile(
    r"(^|[-_./])(kind|minikube|k3d|k3s|docker-desktop|orbstack|microk8s|colima)([-_./]|$)",
    re.IGNORECASE,
)


class ClusterDetector:
    """Detects active Kubernetes cluster contexts and manages ephemeral test namespaces."""

    def __init__(self) -> None:
        self._cached_status: Optional[Dict[str, Any]] = None
        self.last_error: Optional[str] = None
        self._created_namespaces: Set[str] = set()

    @property
    def created_namespaces(self) -> Set[str]:
        """Set of ephemeral namespace names created by this detector instance."""
        return set(self._created_namespaces)

    def get_cluster_status(self, refresh: bool = False) -> Dict[str, Any]:
        """Detect and return the active Kubernetes cluster status.

        Args:
            refresh: If True, bypass the cached status and re-query Kubernetes config.

        Returns:
            Dictionary containing 'available' (bool), 'context' (str), and 'provider' (str).
        """
        if self._cached_status is not None and not refresh:
            return dict(self._cached_status)

        self.last_error = None
        try:
            from kubernetes import config

            contexts, active = config.list_kube_config_contexts()
            if active and active.get("name"):
                active_name = str(active["name"])
                is_local = bool(LOCAL_PROVIDER_REGEX.search(active_name))
                self._cached_status = {
                    "available": True,
                    "context": active_name,
                    "provider": "local" if is_local else "cloud",
                }
            else:
                self._cached_status = {
                    "available": False,
                    "context": "none",
                    "provider": "none",
                }
        except Exception as exc:
            self.last_error = str(exc)
            self._cached_status = {
                "available": False,
                "context": "none",
                "provider": "none",
            }

        return dict(self._cached_status)

    def is_cluster_available(self) -> bool:
        """Check if a Kubernetes cluster context is actively available."""
        return bool(self.get_cluster_status().get("available", False))

    def get_active_context(self) -> Optional[str]:
        """Return the active kubeconfig context name, or None if unavailable."""
        status = self.get_cluster_status()
        if status.get("available") and status.get("context") != "none":
            return status["context"]
        return None

    def create_ephemeral_namespace(
        self, prefix: Optional[str] = DEFAULT_EPHEMERAL_PREFIX, request_timeout: int = 3
    ) -> Optional[str]:
        """Create an ephemeral namespace for isolated testing.

        Args:
            prefix: Name prefix for the temporary namespace.
            request_timeout: HTTP request timeout in seconds.

        Returns:
            The created namespace name, or None if creation failed.
        """
        if not self.is_cluster_available():
            return None

        self.last_error = None
        try:
            # Sanitize prefix to be lowercase DNS-1123 compliant and kubelings-prefixed
            raw = "" if prefix is None else str(prefix)
            clean = re.sub(r"[^a-z0-9-]+", "-", raw.lower()).strip("-")
            if clean in ("", "kubelings"):
                clean = DEFAULT_EPHEMERAL_PREFIX
            elif not clean.startswith("kubelings-"):
                clean = f"kubelings-{clean}".strip("-")

            # Truncate clean prefix to 54 chars so clean + '-' + 8-char uuid <= 63 chars
            clean = clean[:54].rstrip("-")
            if not clean:
                clean = DEFAULT_EPHEMERAL_PREFIX

            from kubernetes import client, config

            config.load_kube_config()
            v1 = client.CoreV1Api()

            ns_name = f"{clean}-{uuid.uuid4().hex[:8]}"
            body = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=ns_name,
                    labels={
                        "app.kubernetes.io/managed-by": "kubelings",
                        "kubelings.dev/ephemeral": "true",
                    },
                )
            )
            v1.create_namespace(body=body, _request_timeout=request_timeout)
            self._created_namespaces.add(ns_name)
            return ns_name
        except Exception as exc:
            self.last_error = str(exc)
            return None

    def cleanup_namespace(self, namespace: str, request_timeout: int = 3) -> bool:
        """Clean up an ephemeral test namespace safely.

        Only namespaces matching the kubelings ephemeral naming convention
        (e.g., matching 'kubelings-*') are permitted to prevent accidental
        deletion of system or user namespaces (e.g. 'default', 'kube-system').

        Args:
            namespace: Name of the namespace to delete.
            request_timeout: HTTP request timeout in seconds.

        Returns:
            True if deletion was successfully initiated, False otherwise.
        """
        if not self.is_cluster_available() or not namespace:
            return False

        self.last_error = None
        # Enforce strict fullmatch safety guard on namespace name
        if not EPHEMERAL_NAMESPACE_PATTERN.fullmatch(namespace):
            self.last_error = (
                f"Refusing to delete non-ephemeral namespace '{namespace}'. "
                "Only namespaces matching 'kubelings-*' can be deleted."
            )
            return False

        try:
            from kubernetes import client, config

            config.load_kube_config()
            v1 = client.CoreV1Api()
            v1.delete_namespace(name=namespace, _request_timeout=request_timeout)
            self._created_namespaces.discard(namespace)
            return True
        except Exception as exc:
            self.last_error = str(exc)
            return False
