"""
Exercise: solutions/05_services_networking/net05.py
Topic: ExternalName Services & Manual Endpoints

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ExternalName
  externalName: db.production.aws.rds.com
---
apiVersion: v1
kind: Service
metadata:
  name: legacy-crm
spec:
  ports:
  - name: http
    port: 80
    targetPort: 8080
---
apiVersion: v1
kind: Endpoints
metadata:
  name: legacy-crm
subsets:
- addresses:
  - ip: 10.240.0.15
  - ip: 10.240.0.16
  ports:
  - name: http
    port: 8080
"""


def validate_endpoints_match_service(service: Dict[str, Any], endpoints: Dict[str, Any]) -> bool:
    """Verify that a manual Endpoints object matches its corresponding Service definition."""
    svc_name = service.get("metadata", {}).get("name")
    ep_name = endpoints.get("metadata", {}).get("name")
    if not svc_name or svc_name != ep_name:
        return False

    svc_ports = {p.get("targetPort", p.get("port")) for p in service.get("spec", {}).get("ports", [])}
    ep_ports = set()
    for subset in endpoints.get("subsets", []):
        for p in subset.get("ports", []):
            ep_ports.add(p.get("port"))

    return bool(svc_ports.intersection(ep_ports))


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 3, "Must define 3 manifests (ExternalName Svc, Selectorless Svc, Endpoints)"
    validate_manifests(manifests, expected_kinds=["Service", "Service", "Endpoints"])

    ext_svc, crm_svc, endpoints = manifests[0], manifests[1], manifests[2]

    assert ext_svc["metadata"]["name"] == "external-database"
    assert ext_svc["spec"]["type"] == "ExternalName"
    assert ext_svc["spec"]["externalName"] == "db.production.aws.rds.com"

    assert crm_svc["metadata"]["name"] == "legacy-crm"
    assert "selector" not in crm_svc.get("spec", {}), "Service must be selectorless"

    assert endpoints["metadata"]["name"] == "legacy-crm"
    addresses = [a["ip"] for a in endpoints["subsets"][0]["addresses"]]
    assert "10.240.0.15" in addresses
    assert "10.240.0.16" in addresses
    assert endpoints["subsets"][0]["ports"][0]["port"] == 8080

    assert validate_endpoints_match_service(crm_svc, endpoints) is True

    # Test mismatched endpoints name
    bad_ep = yaml.safe_load(yaml.dump(endpoints))
    bad_ep["metadata"]["name"] = "other-service"
    assert validate_endpoints_match_service(crm_svc, bad_ep) is False

    print("✓ net05 passed!")


if __name__ == "__main__":
    verify()
