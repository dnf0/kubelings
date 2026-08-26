"""
Exercise: exercises/05_services_networking/net05.py
Topic: ExternalName Services & Manual Endpoints

Instructions:
Kubernetes allows routing to non-cluster resources using:
1. `ExternalName`: An alias that CoreDNS resolves as a CNAME directly to an external hostname (no proxying).
2. Service without selectors: An abstract Service coupled with a manually managed `Endpoints` object
   pointing to static IP addresses (e.g., legacy bare-metal servers or external databases).

1. Define Service 1 'external-database':
   - type: ExternalName
   - externalName: 'db.production.aws.rds.com'
2. Define Service 2 'legacy-crm':
   - without any selector
   - port 80, targetPort 8080
3. Define Endpoints 'legacy-crm':
   - name matching Service 'legacy-crm'
   - subsets with IP addresses ['10.240.0.15', '10.240.0.16'] and port 8080
4. Implement `validate_endpoints_match_service(service, endpoints)`:
   - Returns True if metadata.name matches and endpoint port matches service targetPort (or port).
"""

# I AM NOT DONE

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ???
  externalName: ???
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
  name: ???
subsets:
- addresses:
  - ip: 10.240.0.15
  - ip: 10.240.0.16
  ports:
  - name: http
    port: 0
"""


def validate_endpoints_match_service(service: Dict[str, Any], endpoints: Dict[str, Any]) -> bool:
    """Verify that a manual Endpoints object matches its corresponding Service definition."""
    # TODO: Implement validation
    return False


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 3, (
        "Must define 3 manifests (ExternalName Svc, Selectorless Svc, Endpoints)"
    )
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
