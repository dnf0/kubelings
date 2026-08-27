"""
Solution: crossplane03.py
Topic: Crossplane - ProviderConfig and Resource Deletion Policies
"""


def build_provider_and_resource() -> list[dict]:
    provider_config = {
        "apiVersion": "aws.upbound.io/v1beta1",
        "kind": "ProviderConfig",
        "metadata": {
            "name": "default-aws-provider",
        },
        "spec": {
            "credentials": {
                "source": "Secret",
                "secretRef": {
                    "namespace": "crossplane-system",
                    "name": "aws-credentials",
                    "key": "creds",
                },
            },
        },
    }

    bucket = {
        "apiVersion": "s3.aws.upbound.io/v1beta1",
        "kind": "Bucket",
        "metadata": {
            "name": "app-assets-bucket",
        },
        "spec": {
            "providerConfigRef": {
                "name": "default-aws-provider",
            },
            "deletionPolicy": "Delete",
        },
    }

    return [provider_config, bucket]


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
