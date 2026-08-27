"""
Exercise: exercises/05_services_networking/net03.py
Topic: NodePort & LoadBalancer Service Types

Instructions:
Kubernetes provides external connectivity using:
- NodePort: Allocates a dedicated high port (default range 30000-32767) on every node in the cluster.
- LoadBalancer: Provisions a cloud provider load balancer that forwards external traffic to NodePorts.

1. Configure Service 1 'frontend-np':
   - type: NodePort
   - selector: {app: 'frontend'}
   - ports: name 'http', port 80, targetPort 80, nodePort 30080
2. Configure Service 2 'frontend-lb':
   - type: LoadBalancer
   - selector: {app: 'frontend'}
   - ports: name 'https', port 443, targetPort 8443
   - loadBalancerSourceRanges: ['192.168.0.0/16', '10.0.0.0/8']
3. Implement `validate_node_port_range(port)`:
   - Returns True if port is between 30000 and 32767 (inclusive), otherwise False.
"""

import yaml

from kubelings.validator import validate_manifests

SERVICES_MANIFEST = """
apiVersion: v1
kind: Service
metadata:
  name: frontend-np
spec:
  type: ???
  selector:
    app: frontend
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 0
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-lb
spec:
  type: ???
  selector:
    app: frontend
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 8443
  loadBalancerSourceRanges:
    - 192.168.0.0/16
    - 10.0.0.0/8
"""


def validate_node_port_range(port: int) -> bool:
    """Validate whether port falls within standard Kubernetes NodePort range (30000-32767)."""
    # TODO: Implement range check
    return False


def verify():
    manifests = list(yaml.safe_load_all(SERVICES_MANIFEST))
    assert len(manifests) == 2, "Must define 2 services (NodePort and LoadBalancer)"
    validate_manifests(manifests, expected_kinds=["Service", "Service"])

    np_svc, lb_svc = manifests[0], manifests[1]

    assert np_svc["metadata"]["name"] == "frontend-np"
    assert np_svc["spec"]["type"] == "NodePort"
    assert np_svc["spec"]["ports"][0]["nodePort"] == 30080
    assert validate_node_port_range(np_svc["spec"]["ports"][0]["nodePort"]) is True

    assert lb_svc["metadata"]["name"] == "frontend-lb"
    assert lb_svc["spec"]["type"] == "LoadBalancer"
    assert lb_svc["spec"]["ports"][0]["port"] == 443
    assert lb_svc["spec"]["ports"][0]["targetPort"] == 8443
    assert "192.168.0.0/16" in lb_svc["spec"]["loadBalancerSourceRanges"]

    # Test range check helper
    assert validate_node_port_range(30000) is True
    assert validate_node_port_range(32767) is True
    assert validate_node_port_range(80) is False
    assert validate_node_port_range(29999) is False
    assert validate_node_port_range(32768) is False

    print("✓ net03 passed!")


if __name__ == "__main__":
    verify()
