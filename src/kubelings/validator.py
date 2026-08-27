"""Kubernetes Manifest & Schema Validator for Kubelings."""

from typing import Any, Dict, List, Optional, Tuple

import yaml

VALID_MATCH_EXPRESSION_OPERATORS = {"In", "NotIn", "Exists", "DoesNotExist"}


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

            if match_labels is not None and not isinstance(match_labels, dict):
                raise ManifestValidationError(
                    f"Manifest 'spec.selector.matchLabels' must be a dictionary for {kind}."
                )
            if match_expressions is not None:
                if not isinstance(match_expressions, list):
                    raise ManifestValidationError(
                        f"Manifest 'spec.selector.matchExpressions' must be a list for {kind}."
                    )
                for idx, expr in enumerate(match_expressions):
                    if not isinstance(expr, dict):
                        raise ManifestValidationError(
                            f"Expression at index {idx} in 'spec.selector.matchExpressions' "
                            "must be a dictionary."
                        )
                    key_val = expr.get("key")
                    if not key_val or not isinstance(key_val, str) or not key_val.strip():
                        raise ManifestValidationError(
                            f"Expression at index {idx} in 'spec.selector.matchExpressions' "
                            "missing non-empty 'key'."
                        )
                    op_val = expr.get("operator")
                    if op_val not in VALID_MATCH_EXPRESSION_OPERATORS:
                        raise ManifestValidationError(
                            f"Expression at index {idx} has invalid operator '{op_val}'. "
                            f"Must be one of {sorted(VALID_MATCH_EXPRESSION_OPERATORS)}."
                        )
                    if op_val in {"In", "NotIn"}:
                        values = expr.get("values")
                        if not isinstance(values, list) or len(values) == 0:
                            raise ManifestValidationError(
                                f"Expression with operator '{op_val}' must define "
                                "a non-empty list of 'values'."
                            )

            if not match_labels and not match_expressions:
                raise ManifestValidationError(
                    f"Manifest 'spec.selector' for {kind} must define "
                    "'matchLabels' or 'matchExpressions'."
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

    elif kind == "RayCluster":
        ray_errs = _validate_ray_cluster(manifest)
        if ray_errs:
            raise ManifestValidationError("; ".join(ray_errs))

    elif kind == "RayJob":
        ray_errs = _validate_ray_job(manifest)
        if ray_errs:
            raise ManifestValidationError("; ".join(ray_errs))

    elif kind == "RayService":
        ray_errs = _validate_ray_service(manifest)
        if ray_errs:
            raise ManifestValidationError("; ".join(ray_errs))

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


def _validate_ray_cluster(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate a ray.io/v1 RayCluster manifest."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not api_version.startswith("ray.io/"):
        errors.append(f"RayCluster 'apiVersion' must be under 'ray.io/', got '{api_version}'.")

    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        errors.append("RayCluster 'spec' must be a dictionary.")
        return errors

    head_group = spec.get("headGroupSpec")
    if not isinstance(head_group, dict):
        errors.append("RayCluster 'spec.headGroupSpec' must be a dictionary.")
    else:
        template = head_group.get("template")
        if not isinstance(template, dict) or not isinstance(template.get("spec"), dict):
            errors.append("RayCluster 'spec.headGroupSpec.template.spec' must be a dictionary.")
        else:
            try:
                _validate_pod_spec(template["spec"], "spec.headGroupSpec.template.spec")
            except ManifestValidationError as e:
                errors.append(str(e))

    worker_groups = spec.get("workerGroupSpecs")
    if not isinstance(worker_groups, list) or len(worker_groups) == 0:
        errors.append("RayCluster 'spec.workerGroupSpecs' must be a non-empty list.")
    else:
        group_names: set[str] = set()
        has_gpu_worker = False

        for idx, wg in enumerate(worker_groups):
            if not isinstance(wg, dict):
                errors.append(f"Worker group at index {idx} must be a dictionary.")
                continue
            name = wg.get("groupName")
            if not name or not isinstance(name, str) or not name.strip():
                errors.append(f"Worker group at index {idx} missing required string 'groupName'.")
            else:
                group_names.add(name)

            replicas = wg.get("replicas")
            if replicas is not None and (type(replicas) is not int or replicas < 0):
                errors.append(f"Worker group '{name}' replicas must be a non-negative integer.")

            min_rep = wg.get("minReplicas")
            max_rep = wg.get("maxReplicas")
            if min_rep is not None and (type(min_rep) is not int or min_rep < 0):
                errors.append(f"Worker group '{name}' minReplicas must be a non-negative integer.")
            if max_rep is not None and (type(max_rep) is not int or max_rep < 0):
                errors.append(f"Worker group '{name}' maxReplicas must be a non-negative integer.")
            if min_rep is not None and max_rep is not None and min_rep > max_rep:
                errors.append(
                    f"Worker group '{name}' minReplicas ({min_rep}) cannot exceed maxReplicas ({max_rep})."
                )

            template = wg.get("template")
            if not isinstance(template, dict) or not isinstance(template.get("spec"), dict):
                errors.append(f"Worker group '{name}' template.spec must be a dictionary.")
            else:
                try:
                    _validate_pod_spec(template["spec"], f"workerGroupSpecs[{idx}].template.spec")
                except ManifestValidationError as e:
                    errors.append(str(e))

                containers = template["spec"].get("containers", [])
                if isinstance(containers, list):
                    for c in containers:
                        if isinstance(c, dict):
                            resources = c.get("resources", {})
                            if isinstance(resources, dict):
                                limits = resources.get("limits", {})
                                requests = resources.get("requests", {})
                                if (
                                    isinstance(limits, dict)
                                    and any("gpu" in str(k).lower() for k in limits)
                                ) or (
                                    isinstance(requests, dict)
                                    and any("gpu" in str(k).lower() for k in requests)
                                ):
                                    has_gpu_worker = True

        if exercise_name == "ray02":
            if len(worker_groups) < 2:
                errors.append(
                    "Exercise ray02 requires heterogeneous worker pools (at least 2 worker groups)."
                )
            if len(group_names) < len(worker_groups):
                errors.append("Worker groups must have distinct group names.")
            if not has_gpu_worker:
                errors.append(
                    "Heterogeneous RayCluster in ray02 must include a GPU worker group with nvidia.com/gpu."
                )

    return errors


def _validate_ray_job(manifest: Dict[str, Any], exercise_name: Optional[str] = None) -> List[str]:
    """Validate a ray.io/v1 RayJob manifest."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not api_version.startswith("ray.io/"):
        errors.append(f"RayJob 'apiVersion' must be under 'ray.io/', got '{api_version}'.")

    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        errors.append("RayJob 'spec' must be a dictionary.")
        return errors

    entrypoint = spec.get("entrypoint")
    if not entrypoint or not isinstance(entrypoint, str) or not entrypoint.strip():
        errors.append("RayJob 'spec.entrypoint' must be a non-empty command string.")

    cluster_spec = spec.get("rayClusterSpec")
    cluster_selector = spec.get("clusterSelector")
    if not cluster_spec and not cluster_selector:
        errors.append("RayJob must define either 'spec.rayClusterSpec' or 'spec.clusterSelector'.")

    if cluster_spec is not None:
        if not isinstance(cluster_spec, dict):
            errors.append("RayJob 'spec.rayClusterSpec' must be a dictionary.")
        else:
            head_group = cluster_spec.get("headGroupSpec")
            if not isinstance(head_group, dict):
                errors.append("RayJob 'spec.rayClusterSpec.headGroupSpec' must be a dictionary.")
            else:
                template = head_group.get("template")
                if not isinstance(template, dict) or not isinstance(template.get("spec"), dict):
                    errors.append(
                        "RayJob 'spec.rayClusterSpec.headGroupSpec.template.spec' must be a dictionary."
                    )
                else:
                    try:
                        _validate_pod_spec(
                            template["spec"],
                            "spec.rayClusterSpec.headGroupSpec.template.spec",
                        )
                    except ManifestValidationError as e:
                        errors.append(str(e))

    if exercise_name == "ray03":
        if spec.get("shutdownAfterJobFinishes") is not True:
            errors.append("Exercise ray03 requires 'spec.shutdownAfterJobFinishes' set to true.")
        ttl = spec.get("ttlSecondsAfterFinished")
        if ttl is None or type(ttl) is not int or ttl < 0:
            errors.append(
                "Exercise ray03 requires 'spec.ttlSecondsAfterFinished' set to a positive integer."
            )

    return errors


def _validate_ray_service(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate a ray.io/v1 RayService manifest."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not api_version.startswith("ray.io/"):
        errors.append(f"RayService 'apiVersion' must be under 'ray.io/', got '{api_version}'.")

    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        errors.append("RayService 'spec' must be a dictionary.")
        return errors

    cluster_spec = spec.get("rayClusterSpec")
    if not isinstance(cluster_spec, dict):
        errors.append("RayService 'spec.rayClusterSpec' must be a dictionary.")
    else:
        head_group = cluster_spec.get("headGroupSpec")
        if not isinstance(head_group, dict):
            errors.append("RayService 'spec.rayClusterSpec.headGroupSpec' must be a dictionary.")
        else:
            template = head_group.get("template")
            if not isinstance(template, dict) or not isinstance(template.get("spec"), dict):
                errors.append(
                    "RayService 'spec.rayClusterSpec.headGroupSpec.template.spec' must be a dictionary."
                )
            else:
                try:
                    _validate_pod_spec(
                        template["spec"],
                        "spec.rayClusterSpec.headGroupSpec.template.spec",
                    )
                except ManifestValidationError as e:
                    errors.append(str(e))

    serve_config = spec.get("serveConfigV2")
    if not serve_config:
        errors.append("RayService must define 'spec.serveConfigV2'.")
    else:
        parsed_config = None
        if isinstance(serve_config, str):
            try:
                parsed_config = yaml.safe_load(serve_config)
            except Exception as e:
                errors.append(f"RayService 'spec.serveConfigV2' YAML string parsing error: {e}")
        elif isinstance(serve_config, dict):
            parsed_config = serve_config
        else:
            errors.append("RayService 'spec.serveConfigV2' must be a YAML string or dictionary.")

        if isinstance(parsed_config, dict):
            apps = parsed_config.get("applications")
            if not isinstance(apps, list) or len(apps) == 0:
                errors.append(
                    "RayService serveConfigV2 must define a non-empty 'applications' list."
                )
            else:
                for idx, app in enumerate(apps):
                    if not isinstance(app, dict):
                        errors.append(
                            f"Application at index {idx} in serveConfigV2 must be a dictionary."
                        )
                        continue
                    if not app.get("name"):
                        errors.append(
                            f"Application at index {idx} in serveConfigV2 missing 'name'."
                        )
                    if "route_prefix" not in app and "routePrefix" not in app:
                        errors.append(
                            f"Application at index {idx} in serveConfigV2 missing 'route_prefix'."
                        )
                    if "import_path" not in app and "importPath" not in app:
                        errors.append(
                            f"Application at index {idx} in serveConfigV2 missing 'import_path'."
                        )

    return errors


def validate_manifest_dict(
    manifest: Any,
    exercise_name: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """Validate a parsed manifest dictionary against schema rules and exercise criteria.

    Returns:
        (True, []) if valid, or (False, [error_messages]) if invalid.
    """
    if not isinstance(manifest, dict):
        return False, ["Manifest must be a dictionary."]

    if not manifest:
        return False, ["Manifest dictionary cannot be empty."]

    errors: List[str] = []
    for key in ("apiVersion", "kind", "metadata"):
        if key not in manifest:
            errors.append(f"Manifest missing required root key '{key}'.")

    if errors:
        return False, errors

    kind = manifest.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        return False, ["Manifest 'kind' must be a non-empty string."]

    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict):
        return False, ["Manifest 'metadata' must be a dictionary."]

    name = metadata.get("name")
    generate_name = metadata.get("generateName")
    if not (name and isinstance(name, str) and name.strip()) and not (
        generate_name and isinstance(generate_name, str) and generate_name.strip()
    ):
        return False, ["Manifest metadata must define a non-empty string 'name' or 'generateName'."]

    # Ray validation
    if kind == "RayCluster":
        ray_errors = _validate_ray_cluster(manifest, exercise_name)
        if ray_errors:
            return False, ray_errors
        return True, []
    elif kind == "RayJob":
        ray_errors = _validate_ray_job(manifest, exercise_name)
        if ray_errors:
            return False, ray_errors
        return True, []
    elif kind == "RayService":
        ray_errors = _validate_ray_service(manifest, exercise_name)
        if ray_errors:
            return False, ray_errors
        return True, []

    # Standard Kubernetes validation
    try:
        validate_manifest(manifest)
    except ManifestValidationError as e:
        return False, [str(e)]

    return True, []


def validate_manifest_text(
    yaml_text: str,
    exercise_name: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """Validate YAML text containing one or more Kubernetes/CRD manifests.

    Args:
        yaml_text: The YAML string to validate.
        exercise_name: Optional exercise identifier for specific rule enforcement.

    Returns:
        (True, []) if all manifests pass, or (False, [error_messages]) on failure.
    """
    if not yaml_text or not yaml_text.strip():
        return False, ["Manifest text cannot be empty."]

    try:
        parsed_docs = list(yaml.safe_load_all(yaml_text))
    except Exception as e:
        return False, [f"YAML parsing error: {e}"]

    docs = [d for d in parsed_docs if d is not None]
    if not docs:
        return False, ["No valid YAML documents found in manifest text."]

    all_errors: List[str] = []
    for doc in docs:
        passed, doc_errors = validate_manifest_dict(doc, exercise_name)
        if not passed:
            all_errors.extend(doc_errors)

    if all_errors:
        return False, all_errors
    return True, []
