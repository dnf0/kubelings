# I AM NOT DONE
"""
Exercise: Strict Mutual TLS & PeerAuthentication (mesh02)

Service meshes enforce end-to-end cryptographic identity and encryption via mTLS.
In Istio and Cilium Service Mesh, `PeerAuthentication` defines the mTLS enforcement mode.

Task:
Complete `get_peer_authentication_manifest()` to enforce STRICT mTLS for the `production` namespace:
1. apiVersion: "security.istio.io/v1beta1"
2. kind: "PeerAuthentication"
3. metadata:
   - name: "default"
   - namespace: "production"
4. spec:
   - mtls:
     - mode: "STRICT"
"""

from typing import Any, Dict


def get_peer_authentication_manifest() -> Dict[str, Any]:
    # TODO: Define and return the PeerAuthentication manifest dictionary
    return {}


def verify() -> None:
    manifest = get_peer_authentication_manifest()
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "security.istio.io/v1beta1"
    assert manifest.get("kind") == "PeerAuthentication"

    meta = manifest.get("metadata", {})
    assert meta.get("name") == "default"
    assert meta.get("namespace") == "production"

    spec = manifest.get("spec", {})
    mtls = spec.get("mtls", {})
    assert mtls.get("mode") == "STRICT", "Expected mtls.mode to be 'STRICT'"

    print("✓ Strict PeerAuthentication mTLS policy validated successfully!")


if __name__ == "__main__":
    verify()
