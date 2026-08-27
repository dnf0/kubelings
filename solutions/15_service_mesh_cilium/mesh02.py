"""
Solution: Strict Mutual TLS & PeerAuthentication (mesh02)
"""

from typing import Any, Dict


def get_peer_authentication_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "security.istio.io/v1beta1",
        "kind": "PeerAuthentication",
        "metadata": {
            "name": "default",
            "namespace": "production",
        },
        "spec": {
            "mtls": {
                "mode": "STRICT",
            }
        },
    }


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
