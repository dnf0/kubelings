"""Kubernetes Manifest & Schema Validator for Kubelings."""

from typing import Any, List, Optional


class ManifestValidationError(ValueError):
    """Raised when a Kubernetes manifest fails schema validation."""


def _validate_containers(
    containers: Any,
    context_name: str = "containers",
    allow_empty: bool = False,
) -> None:
    """Validate a list of container definitions."""
    if not isinstance(containers, list):
        raise ManifestValidationError(f"Manifest '{context_name}' must be a list.")

    if not allow_empty and len(containers) == 0:
        raise ManifestValidationError(f"Manifest '{context_name}' must be a non-empty list.")

    for idx, c in enumerate(containers):
        if not isinstance(c, dict):
            raise ManifestValidationError(
                f"Container at index {idx} in '{context_name}' must be a dictionary."
            )
        name = c.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            raise ManifestValidationError(
                f"Container at index {idx} in '{context_name}' missing required non-empty 'name'."
            )
        image = c.get("image")
        if not image or not isinstance(image, str) or not image.strip():
            raise ManifestValidationError(
                f"Container '{name.strip()}' in '{context_name}' missing required non-empty 'image'."
            )


def _validate_pod_spec(spec: Any, context_name: str = "spec") -> None:
    """Validate a PodSpec dictionary structure."""
    if not isinstance(spec, dict):
        raise ManifestValidationError(f"Manifest '{context_name}' must be a dictionary.")

    _validate_containers(spec.get("containers"), f"{context_name}.containers", allow_empty=False)

    if "initContainers" in spec:
        _validate_containers(
            spec.get("initContainers"),
            f"{context_name}.initContainers",
            allow_empty=True,
        )


def validate_manifest(
    manifest: Any,
    expected_kind: Optional[str] = None,
    expected_api_version: Optional[str] = None,
) -> bool:
    """Validate a single Kubernetes manifest dictionary against schema rules.

    Args:
        manifest: The parsed Kubernetes manifest (must be a dict).
        expected_kind: Optional Kubernetes Kind that this manifest must match.
        expected_api_version: Optional apiVersion that this manifest must match.

    Returns:
        True if the manifest is valid.

    Raises:
        ManifestValidationError: If the manifest fails schema checks.
    """
    if not isinstance(manifest, dict):
        raise ManifestValidationError("Manifest must be a dictionary.")

    if not manifest:
        raise ManifestValidationError("Manifest dictionary cannot be empty.")

    for key in ("apiVersion", "kind", "metadata"):
        if key not in manifest:
            raise ManifestValidationError(f"Manifest missing required root key '{key}'.")

    kind = manifest.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        raise ManifestValidationError("Manifest 'kind' must be a non-empty string.")

    api_version = manifest.get("apiVersion")
    if not isinstance(api_version, str) or not api_version.strip():
        raise ManifestValidationError("Manifest 'apiVersion' must be a non-empty string.")

    if expected_kind and kind != expected_kind:
        raise ManifestValidationError(f"Expected kind '{expected_kind}', got '{kind}'.")

    if expected_api_version and api_version != expected_api_version:
        raise ManifestValidationError(
            f"Expected apiVersion '{expected_api_version}', got '{api_version}'."
        )

    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict):
        raise ManifestValidationError("Manifest 'metadata' must be a dictionary.")

    name = metadata.get("name")
    generate_name = metadata.get("generateName")
    has_valid_name = bool(name and isinstance(name, str) and name.strip())
    has_valid_gen_name = bool(
        generate_name and isinstance(generate_name, str) and generate_name.strip()
    )

    if not has_valid_name and not has_valid_gen_name:
        raise ManifestValidationError(
            "Manifest metadata must define a non-empty string 'name' or 'generateName'."
        )

    if "labels" in metadata and not isinstance(metadata["labels"], dict):
        raise ManifestValidationError("Manifest metadata.labels must be a dictionary.")

    if "annotations" in metadata and not isinstance(metadata["annotations"], dict):
        raise ManifestValidationError("Manifest metadata.annotations must be a dictionary.")

    # Kind-specific schema checks
    if kind == "Pod":
        _validate_pod_spec(manifest.get("spec"), "spec")

    elif kind in ("Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Job"):
        spec = manifest.get("spec")
        if not isinstance(spec, dict):
            raise ManifestValidationError(f"Manifest 'spec' must be a dictionary for {kind}.")

        template = spec.get("template")
        if not isinstance(template, dict):
            raise ManifestValidationError(
                f"Manifest 'spec.template' must be a dictionary for {kind}."
            )
        template_spec = template.get("spec")
        if not isinstance(template_spec, dict):
            raise ManifestValidationError(
                f"Manifest 'spec.template.spec' must be a dictionary for {kind}."
            )
        _validate_pod_spec(template_spec, "spec.template.spec")

        if kind in ("Deployment", "StatefulSet", "DaemonSet", "ReplicaSet"):
            selector = spec.get("selector")
            if not isinstance(selector, dict):
                raise ManifestValidationError(
                    f"Manifest 'spec.selector' must be a dictionary for {kind}."
                )
            match_labels = selector.get("matchLabels")
            match_expressions = selector.get("matchExpressions")
            if not match_labels and not match_expressions:
                raise ManifestValidationError(
                    f"Manifest 'spec.selector' for {kind} must define 'matchLabels' or 'matchExpressions'."
                )
            if isinstance(match_labels, dict):
                template_meta = template.get("metadata") or {}
                template_labels = (
                    template_meta.get("labels") if isinstance(template_meta, dict) else {}
                )
                if not isinstance(template_labels, dict) or not all(
                    template_labels.get(k) == v for k, v in match_labels.items()
                ):
                    raise ManifestValidationError(
                        f"Pod template labels in {kind} must match 'spec.selector.matchLabels'."
                    )

        if kind == "StatefulSet":
            service_name = spec.get("serviceName")
            if not service_name or not isinstance(service_name, str) or not service_name.strip():
                raise ManifestValidationError(
                    "StatefulSet must define a non-empty string 'spec.serviceName'."
                )

    elif kind == "CronJob":
        spec = manifest.get("spec")
        if not isinstance(spec, dict):
            raise ManifestValidationError("Manifest 'spec' must be a dictionary for CronJob.")
        schedule = spec.get("schedule")
        if not schedule or not isinstance(schedule, str) or not schedule.strip():
            raise ManifestValidationError(
                "CronJob 'spec.schedule' must be a non-empty cron expression string."
            )
        job_template = spec.get("jobTemplate")
        if not isinstance(job_template, dict):
            raise ManifestValidationError("CronJob 'spec.jobTemplate' must be a dictionary.")
        jt_spec = job_template.get("spec")
        if not isinstance(jt_spec, dict):
            raise ManifestValidationError("CronJob 'spec.jobTemplate.spec' must be a dictionary.")
        jt_template = jt_spec.get("template")
        if not isinstance(jt_template, dict):
            raise ManifestValidationError(
                "CronJob 'spec.jobTemplate.spec.template' must be a dictionary."
            )
        jt_template_spec = jt_template.get("spec")
        if not isinstance(jt_template_spec, dict):
            raise ManifestValidationError(
                "CronJob 'spec.jobTemplate.spec.template.spec' must be a dictionary."
            )
        _validate_pod_spec(jt_template_spec, "spec.jobTemplate.spec.template.spec")

    elif kind == "Service":
        spec = manifest.get("spec")
        if not isinstance(spec, dict):
            raise ManifestValidationError("Service 'spec' must be a dictionary.")
        if "ports" in spec:
            ports = spec.get("ports")
            if not isinstance(ports, list):
                raise ManifestValidationError("Service 'spec.ports' must be a list.")
            for p in ports:
                if not isinstance(p, dict):
                    raise ManifestValidationError("Each service port must be a dictionary.")
                port_val = p.get("port")
                if type(port_val) is not int or not (1 <= port_val <= 65535):
                    raise ManifestValidationError(
                        "Each service port must define an integer 'port' between 1 and 65535."
                    )

    elif kind == "ConfigMap":
        if "data" in manifest and not isinstance(manifest["data"], dict):
            raise ManifestValidationError("ConfigMap 'data' must be a dictionary.")

    elif kind == "Secret":
        if "data" in manifest and not isinstance(manifest["data"], dict):
            raise ManifestValidationError("Secret 'data' must be a dictionary.")
        if "stringData" in manifest and not isinstance(manifest["stringData"], dict):
            raise ManifestValidationError("Secret 'stringData' must be a dictionary.")

    elif kind in ("Role", "ClusterRole"):
        if "rules" in manifest and not isinstance(manifest["rules"], list):
            raise ManifestValidationError(f"{kind} 'rules' must be a list.")

    elif kind in ("RoleBinding", "ClusterRoleBinding"):
        role_ref = manifest.get("roleRef")
        if not isinstance(role_ref, dict) or not role_ref.get("kind") or not role_ref.get("name"):
            raise ManifestValidationError(
                f"{kind} must define a 'roleRef' dictionary with 'kind' and 'name'."
            )
        if "subjects" in manifest and not isinstance(manifest["subjects"], list):
            raise ManifestValidationError(f"{kind} 'subjects' must be a list.")

    elif kind == "HorizontalPodAutoscaler":
        spec = manifest.get("spec")
        if not isinstance(spec, dict):
            raise ManifestValidationError("HorizontalPodAutoscaler 'spec' must be a dictionary.")
        scale_target = spec.get("scaleTargetRef")
        if (
            not isinstance(scale_target, dict)
            or not scale_target.get("kind")
            or not scale_target.get("name")
        ):
            raise ManifestValidationError(
                "HorizontalPodAutoscaler must define 'spec.scaleTargetRef' with 'kind' and 'name'."
            )

    return True


def validate_manifests(
    manifests: List[Any],
    expected_kinds: Optional[List[str]] = None,
) -> bool:
    """Validate a sequence of Kubernetes manifests (e.g. from multi-doc YAML).

    Args:
        manifests: List of parsed manifest dictionaries.
        expected_kinds: Optional list of expected Kinds in corresponding order.

    Returns:
        True if all manifests are valid.

    Raises:
        ManifestValidationError: If any manifest fails validation or counts mismatch.
    """
    if not isinstance(manifests, list):
        raise ManifestValidationError("Manifests must be provided as a list.")

    if len(manifests) == 0:
        raise ManifestValidationError("Manifests list cannot be empty.")

    if expected_kinds is not None:
        if len(manifests) != len(expected_kinds):
            raise ManifestValidationError(
                f"Expected {len(expected_kinds)} manifests, got {len(manifests)}."
            )
        for m, exp_kind in zip(manifests, expected_kinds):
            validate_manifest(m, expected_kind=exp_kind)
    else:
        for m in manifests:
            validate_manifest(m)

    return True
