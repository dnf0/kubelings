"""
Exercise: exercises/03_config_secrets/config03.py
Topic: Secrets: Base64 Encoding & stringData

Context & Why:
Kubernetes Secrets store sensitive configuration assets such as database credentials, API tokens,
and private encryption keys. In declarative Secret manifests, values in the `data` field must be
base64-encoded strings (allowing arbitrary binary payloads). To simplify manual authoring without
requiring manual base64 pipelines, Kubernetes supports the write-only `stringData` field: the API
server automatically base64-encodes plaintext values in `stringData` and writes them into `data`
before persisting them to etcd. The default Secret type `Opaque` denotes arbitrary user-defined
key-value secret payloads.

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
# TODO: Set type to 'Opaque'
# WHY: 'Opaque' is the standard Kubernetes secret type for unstructured sensitive key-value data.
type: ???
data:
  # TODO: Populate base64-encoded strings for 'username' ('admin') and 'password' ('supersecret')
  # WHY: The Kubernetes Secret data field requires base64-encoded values to support arbitrary binary and textual data over the wire.
  username: ???
  password: ???
stringData:
  api_key: "prod-api-key-998877"
"""


def decode_secret_data(secret_dict: Dict[str, Any]) -> Dict[str, str]:
    """Decode base64 encoded strings in secret['data'] to utf-8 strings."""
    # TODO: Implement base64 decoding logic for all entries in secret['data']
    # WHY: Models how the kubelet decodes secret data payloads before mounting them into container filesystems or env vars.
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
