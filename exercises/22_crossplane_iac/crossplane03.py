# I AM NOT DONE
"""
Exercise: crossplane03.py
Topic: Crossplane - ProviderConfig and Resource Deletion Policies

Task:
Define an AWS ProviderConfig manifest and configure managed resource deletion policy:
1. 'apiVersion': 'aws.upbound.io/v1beta1', 'kind': 'ProviderConfig'
2. Named 'default-aws-provider'
3. 'spec.credentials':
   - 'source': 'Secret'
   - 'secretRef': {'namespace': 'crossplane-system', 'name': 'aws-credentials', 'key': 'creds'}
4. Include a managed S3 Bucket resource:
   - 'apiVersion': 's3.aws.upbound.io/v1beta1', 'kind': 'Bucket'
   - Named 'app-assets-bucket'
   - 'spec.providerConfigRef': {'name': 'default-aws-provider'}
   - 'spec.deletionPolicy': 'Delete' (ensures underlying cloud resource is cleaned up when CR is deleted)
"""

import yaml


def build_provider_and_resource() -> list[dict]:
    # TODO: Define and return list containing ProviderConfig and Bucket manifests
    return []


def verify():
    manifests = build_provider_and_resource()
    assert len(manifests) == 2, f"Expected 2 manifests, found {len(manifests)}"

    pc = next((m for m in manifests if m.get("kind") == "ProviderConfig"), None)
    assert pc is not None, "Missing ProviderConfig manifest"
    assert pc.get("metadata", {}).get("name") == "default-aws-provider"
    creds = pc.get("spec", {}).get("credentials", {})
    assert creds.get("source") == "Secret"
    assert creds.get("secretRef", {}).get("name") == "aws-credentials"
    assert creds.get("secretRef", {}).get("namespace") == "crossplane-system"

    bucket = next((m for m in manifests if m.get("kind") == "Bucket"), None)
    assert bucket is not None, "Missing Bucket manifest"
    assert bucket.get("metadata", {}).get("name") == "app-assets-bucket"
    assert bucket.get("spec", {}).get("providerConfigRef", {}).get("name") == "default-aws-provider"
    assert bucket.get("spec", {}).get("deletionPolicy") == "Delete"

    print("✓ Crossplane ProviderConfig and DeletionPolicy successfully validated!")


if __name__ == "__main__":
    verify()
