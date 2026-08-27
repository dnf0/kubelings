"""
Chapter 19: Package Management with Helm
Exercise 19.3: Helm values.schema.json Validation Schema

Task: Construct a strict JSON Schema (Draft-7) specification for Helm chart values validation.
Requirements:
- $schema: 'http://json-schema.org/draft-07/schema#'
- type: 'object'
- required: ['replicaCount', 'image', 'service']
- properties:
    - replicaCount: type integer, minimum: 1, maximum: 100
    - image: type object, required: ['repository', 'tag']
        - repository: type string
        - tag: type string
    - service: type object, required: ['type', 'port']
        - type: type string, enum: ['ClusterIP', 'NodePort', 'LoadBalancer']
        - port: type integer, minimum: 1, maximum: 65535
"""

from typing import Any, Dict

import jsonschema


def get_values_schema() -> Dict[str, Any]:
    return {}


if __name__ == "__main__":
    schema = get_values_schema()
    assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"
    assert set(schema.get("required", [])) == {"replicaCount", "image", "service"}

    # Valid test case
    valid_payload = {
        "replicaCount": 3,
        "image": {"repository": "nginx", "tag": "1.25"},
        "service": {"type": "ClusterIP", "port": 80},
    }
    jsonschema.validate(instance=valid_payload, schema=schema)

    # Invalid test case: replicaCount out of bounds
    invalid_payload = {
        "replicaCount": 0,
        "image": {"repository": "nginx", "tag": "1.25"},
        "service": {"type": "ClusterIP", "port": 80},
    }
    try:
        jsonschema.validate(instance=invalid_payload, schema=schema)
        raise AssertionError("Expected ValidationError on invalid replicaCount")
    except jsonschema.ValidationError:
        pass

    print("✓ Helm values.schema.json validation passed!")
