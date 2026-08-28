"""
Exercise: Strict Mutual TLS & PeerAuthentication (mesh02)

Context & Why:
By default, inter-pod communication across a Kubernetes cluster overlay network is
unencrypted and unauthenticated at the transport layer, exposing workloads to packet
sniffing and spoofing within shared multi-tenant clusters. Service mesh architectures
solve this by establishing zero-trust cryptographic identities (using SPIFFE IDs embedded
in x509 certificates) and enforcing Mutual TLS (mTLS) for all pod-to-pod traffic.

In service mesh control planes (such as Istio or Cilium Service Mesh), the `PeerAuthentication`
CRD defines the policy for incoming mTLS connections. Setting `mode: STRICT` mandates that
all workloads in the designated namespace reject any non-TLS or unauthenticated plaintext
connections, establishing verifiable workload identity and encryption in transit.

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
    # TODO: Construct and return the dictionary representation of a PeerAuthentication CRD
    #       enforcing STRICT mutual TLS mode in the 'production' namespace.
    # WHY: Strict mTLS guarantees transport layer encryption and cryptographically verifies workload identities
    #      (SPIFFE/x509), completely preventing unauthenticated or eavesdropped plaintext traffic.
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
