"""
Exercise: crossplane03.py
Topic: Crossplane - ProviderConfig and Resource Deletion Policies

Context & Why:
Crossplane providers (e.g. `provider-aws`, `provider-gcp`) require authenticated credentials to
interact with cloud provider APIs and manage cloud resource lifecycles.

Key architecture concepts:
- `ProviderConfig`: Configures authentication context (e.g. AWS IAM credentials, GCP service account
  keys) by referencing a Kubernetes Secret. Managed resources specify `providerConfigRef` to select
  which credentials or accounts to target.
- `deletionPolicy`: Dictates what happens to the underlying cloud resource when its Kubernetes custom
  resource is deleted:
  * `Delete`: The provider actively calls cloud APIs to delete the remote resource (e.g. terminating
    the AWS S3 bucket), ensuring zero orphaned cloud resources and preventing cost leaks.
  * `Orphan`: The Kubernetes resource is deleted while the remote cloud asset remains untouched in
    the cloud provider (useful during migrations).

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
    # TODO: Define and return the list of manifests containing the ProviderConfig and managed S3 Bucket with an explicit Delete policy.
    # WHY: ProviderConfig secures cloud API credentials for Crossplane provider pods, while explicit deletion policies ensure complete
    #      lifecycle synchronization between Kubernetes CRs and remote cloud infrastructure to prevent resource leaks and billing waste.
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
