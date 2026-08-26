import pytest
from kubelings.validator import (
    ManifestValidationError,
    validate_manifest,
    validate_manifests,
)


def test_validate_valid_pod_manifest():
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "test-pod", "labels": {"app": "web"}},
        "spec": {
            "containers": [
                {"name": "web", "image": "nginx:alpine", "ports": [{"containerPort": 80}]}
            ],
            "initContainers": [
                {"name": "init-db", "image": "busybox:latest"}
            ],
        },
    }
    assert validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1") is True


def test_validate_valid_service_manifest():
    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "test-svc"},
        "spec": {
            "selector": {"app": "web"},
            "ports": [{"port": 80, "targetPort": 8080}],
            "type": "ClusterIP",
        },
    }
    assert validate_manifest(manifest, expected_kind="Service") is True


def test_validate_valid_deployment_manifest():
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "web-deploy"},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": "web"}},
            "template": {
                "metadata": {"labels": {"app": "web"}},
                "spec": {
                    "containers": [{"name": "web", "image": "nginx:latest"}]
                },
            },
        },
    }
    assert validate_manifest(manifest, expected_kind="Deployment") is True


def test_validate_valid_statefulset_daemonset_job_cronjob():
    # StatefulSet
    sts = {
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {"name": "db-sts"},
        "spec": {
            "serviceName": "db-service",
            "selector": {"matchLabels": {"app": "db"}},
            "template": {
                "metadata": {"labels": {"app": "db"}},
                "spec": {
                    "containers": [{"name": "db", "image": "postgres:15"}]
                },
            },
        },
    }
    assert validate_manifest(sts, expected_kind="StatefulSet") is True

    # DaemonSet
    ds = {
        "apiVersion": "apps/v1",
        "kind": "DaemonSet",
        "metadata": {"name": "fluentd-ds"},
        "spec": {
            "selector": {"matchLabels": {"name": "fluentd"}},
            "template": {
                "metadata": {"labels": {"name": "fluentd"}},
                "spec": {
                    "containers": [{"name": "fluentd", "image": "fluentd:v1"}]
                },
            },
        },
    }
    assert validate_manifest(ds, expected_kind="DaemonSet") is True

    # Job
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": "pi-job"},
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"name": "pi", "image": "perl:5.34", "command": ["perl", "-Mbignum=p", "-e", "print bpi(2000)"]}],
                    "restartPolicy": "Never",
                }
            }
        },
    }
    assert validate_manifest(job, expected_kind="Job") is True

    # CronJob
    cronjob = {
        "apiVersion": "batch/v1",
        "kind": "CronJob",
        "metadata": {"name": "backup-cron"},
        "spec": {
            "schedule": "0 0 * * *",
            "jobTemplate": {
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [{"name": "backup", "image": "backup:v1"}],
                            "restartPolicy": "OnFailure",
                        }
                    }
                }
            },
        },
    }
    assert validate_manifest(cronjob, expected_kind="CronJob") is True


def test_validate_valid_config_and_security_resources():
    cm = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "app-config"},
        "data": {"config.json": "{\"debug\": true}"},
    }
    assert validate_manifest(cm, expected_kind="ConfigMap") is True

    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": "app-secret"},
        "stringData": {"password": "secret"},
        "type": "Opaque",
    }
    assert validate_manifest(secret, expected_kind="Secret") is True

    role = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "Role",
        "metadata": {"name": "pod-reader"},
        "rules": [{"apiGroups": [""], "resources": ["pods"], "verbs": ["get", "list", "watch"]}],
    }
    assert validate_manifest(role, expected_kind="Role") is True

    role_binding = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {"name": "read-pods"},
        "subjects": [{"kind": "User", "name": "alice", "apiGroup": "rbac.authorization.k8s.io"}],
        "roleRef": {"kind": "Role", "name": "pod-reader", "apiGroup": "rbac.authorization.k8s.io"},
    }
    assert validate_manifest(role_binding, expected_kind="RoleBinding") is True

    hpa = {
        "apiVersion": "autoscaling/v2",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {"name": "web-hpa"},
        "spec": {
            "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": "web-deploy"},
            "minReplicas": 1,
            "maxReplicas": 10,
        },
    }
    assert validate_manifest(hpa, expected_kind="HorizontalPodAutoscaler") is True


def test_validate_manifest_non_dict():
    with pytest.raises(ManifestValidationError, match="dictionary"):
        validate_manifest("not a dict")

    with pytest.raises(ManifestValidationError, match="dictionary"):
        validate_manifest(["list item"])

    with pytest.raises(ManifestValidationError, match="dictionary"):
        validate_manifest(None)


def test_validate_manifest_missing_root_keys():
    with pytest.raises(ManifestValidationError, match="apiVersion"):
        validate_manifest({"kind": "Pod", "metadata": {"name": "p"}})

    with pytest.raises(ManifestValidationError, match="kind"):
        validate_manifest({"apiVersion": "v1", "metadata": {"name": "p"}})

    with pytest.raises(ManifestValidationError, match="metadata"):
        validate_manifest({"apiVersion": "v1", "kind": "Pod"})


def test_validate_manifest_invalid_metadata():
    with pytest.raises(ManifestValidationError, match="metadata"):
        validate_manifest({"apiVersion": "v1", "kind": "Pod", "metadata": "not-a-dict"})

    with pytest.raises(ManifestValidationError, match="name"):
        validate_manifest({"apiVersion": "v1", "kind": "Pod", "metadata": {}})

    with pytest.raises(ManifestValidationError, match="name"):
        validate_manifest({"apiVersion": "v1", "kind": "Pod", "metadata": {"name": ""}})

    with pytest.raises(ManifestValidationError, match="labels"):
        validate_manifest({
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "p", "labels": "invalid"},
            "spec": {"containers": [{"name": "c", "image": "img"}]},
        })


def test_validate_manifest_expected_kind_and_version():
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "p"},
        "spec": {"containers": [{"name": "c", "image": "img"}]},
    }
    with pytest.raises(ManifestValidationError, match="Expected kind 'Deployment'"):
        validate_manifest(manifest, expected_kind="Deployment")

    with pytest.raises(ManifestValidationError, match="Expected apiVersion 'apps/v1'"):
        validate_manifest(manifest, expected_api_version="apps/v1")


def test_validate_manifest_workload_spec_errors():
    # Pod missing spec
    with pytest.raises(ManifestValidationError, match="spec"):
        validate_manifest({"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "p"}})

    # Pod containers empty
    with pytest.raises(ManifestValidationError, match="containers"):
        validate_manifest({
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "p"},
            "spec": {"containers": []},
        })

    # Pod container missing image
    with pytest.raises(ManifestValidationError, match="image"):
        validate_manifest({
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "p"},
            "spec": {"containers": [{"name": "c"}]},
        })

    # Pod container missing name
    with pytest.raises(ManifestValidationError, match="name"):
        validate_manifest({
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "p"},
            "spec": {"containers": [{"image": "img"}]},
        })

    # Deployment missing template
    with pytest.raises(ManifestValidationError, match="template"):
        validate_manifest({
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "d"},
            "spec": {"selector": {"matchLabels": {"app": "a"}}},
        })

    # CronJob missing schedule
    with pytest.raises(ManifestValidationError, match="schedule"):
        validate_manifest({
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {"name": "cj"},
            "spec": {
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{"name": "c", "image": "img"}]
                            }
                        }
                    }
                }
            },
        })


def test_validate_manifests_multi_document():
    doc1 = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "my-svc"},
        "spec": {"ports": [{"port": 80}]},
    }
    doc2 = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "my-deploy"},
        "spec": {
            "selector": {"matchLabels": {"app": "app"}},
            "template": {
                "spec": {"containers": [{"name": "app", "image": "app:v1"}]}
            },
        },
    }
    assert validate_manifests([doc1, doc2], expected_kinds=["Service", "Deployment"]) is True


def test_validate_manifests_errors():
    with pytest.raises(ManifestValidationError, match="list"):
        validate_manifests("not a list")  # type: ignore

    with pytest.raises(ManifestValidationError, match="empty"):
        validate_manifests([])

    doc = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "my-svc"},
        "spec": {"ports": [{"port": 80}]},
    }
    with pytest.raises(ManifestValidationError, match="Expected 2 manifests"):
        validate_manifests([doc], expected_kinds=["Service", "Deployment"])
