"""
Exercise: solutions/03_config_secrets/config03.py
Topic: Secrets: Base64 Encoding & stringData

Reference Solution
"""

import base64
from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest

SECRET_MANIFEST = """
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=
  password: c3VwZXJzZWNyZXQ=
stringData:
  api_key: "prod-api-key-998877"
"""


def decode_secret_data(secret_dict: Dict[str, Any]) -> Dict[str, str]:
    """Decode base64 encoded strings in secret['data'] to utf-8 strings."""
    data = secret_dict.get("data", {})
    decoded: Dict[str, str] = {}
    for k, v in data.items():
        if isinstance(v, str):
            decoded[k] = base64.b64decode(v.encode("utf-8")).decode("utf-8")
    return decoded


def verify():
    manifest = yaml.safe_load(SECRET_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Secret", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "db-credentials"
    assert manifest.get("type") == "Opaque", "Secret type must be 'Opaque'"

    # Verify stringData
    assert manifest.get("stringData", {}).get("api_key") == "prod-api-key-998877"

    # Verify base64 decoding function
    decoded = decode_secret_data(manifest)
    assert decoded.get("username") == "admin", (
        f"Decoded username must be 'admin', got {decoded.get('username')}"
    )
    assert decoded.get("password") == "supersecret", (
        f"Decoded password must be 'supersecret', got {decoded.get('password')}"
    )

    print("✓ config03 passed!")


if __name__ == "__main__":
    verify()
