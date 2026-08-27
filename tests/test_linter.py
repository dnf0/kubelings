"""Tests for Universal Kubernetes Manifest Linter."""

from kubelings.linter import ManifestLinter, LintSeverity


def test_linter_detects_missing_probes_and_security():
    bad_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "insecure-pod"},
        "spec": {
            "containers": [{"name": "web", "image": "nginx"}]
        },
    }
    linter = ManifestLinter()
    diagnostics = linter.lint_manifest(bad_manifest)
    rule_ids = {d.rule_id for d in diagnostics}
    assert "SEC001_RUN_AS_NON_ROOT" in rule_ids
    assert "REL001_MISSING_PROBES" in rule_ids
    assert "RES001_MISSING_LIMITS" in rule_ids


def test_linter_passes_secure_well_formed_manifest():
    good_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "secure-pod"},
        "spec": {
            "securityContext": {"runAsNonRoot": True},
            "containers": [
                {
                    "name": "web",
                    "image": "nginx:alpine",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"cpu": "200m", "memory": "256Mi"},
                    },
                    "livenessProbe": {
                        "httpGet": {"path": "/healthz", "port": 80}
                    },
                    "readinessProbe": {
                        "httpGet": {"path": "/ready", "port": 80}
                    },
                    "securityContext": {
                        "readOnlyRootFilesystem": True,
                        "allowPrivilegeEscalation": False,
                    },
                }
            ],
        },
    }
    linter = ManifestLinter()
    diagnostics = linter.lint_manifest(good_manifest)
    errors = [d for d in diagnostics if d.severity == LintSeverity.ERROR]
    assert len(errors) == 0


def test_linter_checks_missing_metadata_name():
    broken_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {},
        "spec": {"containers": []},
    }
    linter = ManifestLinter()
    diagnostics = linter.lint_manifest(broken_manifest)
    rule_ids = {d.rule_id for d in diagnostics}
    assert "SCH001_MISSING_NAME" in rule_ids
