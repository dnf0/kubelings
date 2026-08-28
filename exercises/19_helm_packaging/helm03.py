"""
Chapter 19: Package Management with Helm
Exercise 19.3: Helm values.schema.json Validation Schema

Context & Why:
In Helm chart distribution, user-provided values in `values.yaml` or via `--set` flags
can easily include invalid types, negative replica counts, illegal port numbers, or missing
mandatory fields. Without schema validation, these errors are only caught during cluster
reconciliation or container runtime crashes, wasting developer time.

Helm addresses this by natively supporting `values.schema.json` following the JSON Schema
Draft-7 standard. When users run `helm lint`, `helm template`, or `helm install`, Helm
automatically validates the input values against the schema before rendering. Restricting
properties with `type`, `minimum`/`maximum`, and `enum` bounds provides clear, immediate feedback
on invalid inputs at the CLI client stage.

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
    # TODO: Construct and return the dictionary representation of a JSON Schema Draft-7 schema for Helm values.
    # WHY: Helm values schemas catch configuration typos, missing mandatory keys, and out-of-range parameters
    #      locally before template rendering or API server submission.
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
