"""
Exercise: exercises/03_config_secrets/config03.py
Topic: Secrets: Base64 Encoding & stringData

Instructions:
Kubernetes Secrets store sensitive configuration (passwords, tokens, keys).
Values in the `data` field must be base64-encoded strings, while values in `stringData`
are automatically encoded by the apiserver upon creation.

1. Complete the Secret manifest below:
   - metadata.name: 'db-credentials'
   - type: 'Opaque'
   - data:
     - username: base64 encoding of 'admin'
     - password: base64 encoding of 'supersecret'
   - stringData:
     - api_key: "prod-api-key-998877"
2. Implement `decode_secret_data` to decode all values in the secret's `data` dictionary.
"""

import base64  # noqa: F401
from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest

SECRET_MANIFEST = """
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: ???
data:
  username: ???
  password: ???
stringData:
  api_key: "prod-api-key-998877"
"""


def decode_secret_data(secret_dict: Dict[str, Any]) -> Dict[str, str]:
    """Decode base64 encoded strings in secret['data'] to utf-8 strings."""
    # TODO: Implement base64 decoding logic
    return {}


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
