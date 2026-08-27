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

    elif kind in ("ResourceClaimTemplate", "ResourceClaim", "DeviceClass"):
        dra_errs = _validate_dra_resource(manifest)
        if dra_errs:
            raise ManifestValidationError("; ".join(dra_errs))

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


def _validate_kueue_resource(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate a kueue.x-k8s.io manifest (ResourceFlavor, ClusterQueue, LocalQueue, WorkloadPriorityClass)."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not api_version.startswith("kueue.x-k8s.io/"):
        errors.append(
            f"Kueue resource 'apiVersion' must be under 'kueue.x-k8s.io/', got '{api_version}'."
        )

    kind = manifest.get("kind", "")
    metadata = manifest.get("metadata", {})
    name = metadata.get("name", "") if isinstance(metadata, dict) else ""

    if kind == "ResourceFlavor":
        if not name or not isinstance(name, str) or not name.strip():
            errors.append("ResourceFlavor must have a non-empty metadata.name.")
        spec = manifest.get("spec")
        if spec is not None and not isinstance(spec, dict):
            errors.append("ResourceFlavor 'spec' must be a dictionary if present.")

    elif kind == "ClusterQueue":
        spec = manifest.get("spec")
        if not isinstance(spec, dict):
            errors.append("ClusterQueue 'spec' must be a dictionary.")
            return errors

        resource_groups = spec.get("resourceGroups")
        if not isinstance(resource_groups, list) or len(resource_groups) == 0:
            errors.append("ClusterQueue 'spec.resourceGroups' must be a non-empty list.")
        else:
            for rg_idx, rg in enumerate(resource_groups):
                if not isinstance(rg, dict):
                    errors.append(f"Resource group at index {rg_idx} must be a dictionary.")
                    continue
                covered = rg.get("coveredResources")
                if not isinstance(covered, list) or len(covered) == 0:
                    errors.append(
                        f"Resource group at index {rg_idx} must define non-empty 'coveredResources'."
                    )
                flavors = rg.get("flavors")
                if not isinstance(flavors, list) or len(flavors) == 0:
                    errors.append(
                        f"Resource group at index {rg_idx} must define non-empty 'flavors'."
                    )
                else:
                    for f_idx, flv in enumerate(flavors):
                        if not isinstance(flv, dict):
                            errors.append(
                                f"Flavor at index {f_idx} in resource group {rg_idx} must be a dictionary."
                            )
                            continue
                        if not flv.get("name"):
                            errors.append(
                                f"Flavor at index {f_idx} in resource group {rg_idx} missing 'name'."
                            )
                        resources = flv.get("resources")
                        if not isinstance(resources, list) or len(resources) == 0:
                            errors.append(
                                f"Flavor '{flv.get('name')}' must define non-empty 'resources'."
                            )
                        else:
                            for r_idx, res in enumerate(resources):
                                if not isinstance(res, dict):
                                    errors.append(
                                        f"Resource at index {r_idx} in flavor '{flv.get('name')}' must be a dictionary."
                                    )
                                    continue
                                r_name = res.get("name")
                                if not r_name:
                                    errors.append(
                                        f"Resource at index {r_idx} in flavor '{flv.get('name')}' missing 'name'."
                                    )
                                if "nominalQuota" not in res:
                                    errors.append(
                                        f"Resource '{r_name}' in flavor '{flv.get('name')}' missing 'nominalQuota'."
                                    )
                                else:
                                    nq = res["nominalQuota"]
                                    if isinstance(nq, (int, float)) and nq < 0:
                                        errors.append(
                                            f"Resource '{r_name}' nominalQuota cannot be negative."
                                        )
                                    elif isinstance(nq, str) and nq.strip().startswith("-"):
                                        errors.append(
                                            f"Resource '{r_name}' nominalQuota cannot be negative."
                                        )
                                if "borrowingLimit" in res:
                                    bl = res["borrowingLimit"]
                                    if isinstance(bl, (int, float)) and bl < 0:
                                        errors.append(
                                            f"Resource '{r_name}' borrowingLimit cannot be negative."
                                        )
                                    elif isinstance(bl, str) and bl.strip().startswith("-"):
                                        errors.append(
                                            f"Resource '{r_name}' borrowingLimit cannot be negative."
                                        )

        if exercise_name == "kueue01":
            cohort = spec.get("cohort")
            if not cohort or not isinstance(cohort, str) or not cohort.strip():
                errors.append(
                    "Exercise kueue01 requires 'spec.cohort' to be defined for borrowing."
                )

    elif kind == "LocalQueue":
        spec = manifest.get("spec")
        if not isinstance(spec, dict):
            errors.append("LocalQueue 'spec' must be a dictionary.")
            return errors
        cluster_queue = spec.get("clusterQueue")
        if not cluster_queue or not isinstance(cluster_queue, str) or not cluster_queue.strip():
            errors.append(
                "LocalQueue 'spec.clusterQueue' must be a non-empty string referencing a ClusterQueue."
            )

    elif kind == "WorkloadPriorityClass":
        val = manifest.get("value")
        if val is None or type(val) is not int:
            errors.append("WorkloadPriorityClass must define an integer 'value'.")

    else:
        errors.append(f"Unknown Kueue kind '{kind}'.")

    return errors


def _validate_volcano_job(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate a batch.volcano.sh/v1alpha1 Volcano Job manifest."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not (
        api_version.startswith("batch.volcano.sh/") or api_version.startswith("volcano.sh/")
    ):
        errors.append(
            f"Volcano Job 'apiVersion' must be under 'batch.volcano.sh/', got '{api_version}'."
        )

    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        errors.append("Volcano Job 'spec' must be a dictionary.")
        return errors

    min_available = spec.get("minAvailable")
    if min_available is None or type(min_available) is not int or min_available < 1:
        errors.append("Volcano Job must define a positive integer 'spec.minAvailable'.")

    tasks = spec.get("tasks")
    if not isinstance(tasks, list) or len(tasks) == 0:
        errors.append("Volcano Job must define a non-empty 'spec.tasks' list.")
    else:
        total_replicas = 0
        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                errors.append(f"Task at index {idx} in Volcano Job must be a dictionary.")
                continue
            t_name = task.get("name")
            if not t_name or not isinstance(t_name, str) or not t_name.strip():
                errors.append(f"Task at index {idx} missing required string 'name'.")
            replicas = task.get("replicas", 1)
            if type(replicas) is not int or replicas < 1:
                errors.append(f"Task '{t_name}' replicas must be a positive integer.")
            else:
                total_replicas += replicas

            template = task.get("template")
            if not isinstance(template, dict) or not isinstance(template.get("spec"), dict):
                errors.append(f"Task '{t_name}' must define a valid 'template.spec'.")
            else:
                try:
                    _validate_pod_spec(template["spec"], f"tasks[{idx}].template.spec")
                except ManifestValidationError as e:
                    errors.append(str(e))

        if min_available is not None and isinstance(min_available, int):
            if total_replicas < min_available:
                errors.append(
                    f"Volcano Job gang scheduling invariant violated: total task replicas ({total_replicas}) "
                    f"is less than minAvailable ({min_available})."
                )

    if exercise_name == "volcano01":
        if min_available != 4:
            errors.append("Exercise volcano01 requires 'spec.minAvailable: 4'.")

    return errors


def _validate_volcano_queue(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate a Volcano Queue manifest (scheduling.volcano.sh/v1beta1 or batch.volcano.sh/v1alpha1)."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not (
        api_version.startswith("scheduling.volcano.sh/")
        or api_version.startswith("batch.volcano.sh/")
        or api_version.startswith("volcano.sh/")
    ):
        errors.append(
            f"Volcano Queue 'apiVersion' must be under 'scheduling.volcano.sh/' or 'batch.volcano.sh/', got '{api_version}'."
        )

    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        errors.append("Volcano Queue 'spec' must be a dictionary.")
        return errors

    weight = spec.get("weight")
    if weight is None or not isinstance(weight, (int, float)) or weight <= 0:
        errors.append("Volcano Queue must define a positive number 'spec.weight'.")

    capability = spec.get("capability")
    if capability is not None:
        if not isinstance(capability, dict):
            errors.append("Volcano Queue 'spec.capability' must be a dictionary.")
        else:
            for res_name, quota in capability.items():
                if isinstance(quota, (int, float)) and quota < 0:
                    errors.append(
                        f"Volcano Queue capability '{res_name}' quota cannot be negative."
                    )
                elif isinstance(quota, str) and quota.strip().startswith("-"):
                    errors.append(
                        f"Volcano Queue capability '{res_name}' quota cannot be negative."
                    )

    if exercise_name == "volcano02":
        if not capability or not isinstance(capability, dict):
            errors.append("Exercise volcano02 requires 'spec.capability' resource limits.")

    return errors


def _validate_dra_resource(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate Dynamic Resource Allocation (DRA) manifests (resource.k8s.io/*)."""
    errors: List[str] = []
    api_version = manifest.get("apiVersion", "")
    if not isinstance(api_version, str) or not (
        api_version.startswith("resource.k8s.io/") or "resource.k8s.io" in api_version
    ):
        errors.append(
            f"DRA resource 'apiVersion' must be under 'resource.k8s.io/', got '{api_version}'."
        )

    kind = manifest.get("kind", "")
    spec = manifest.get("spec")
    if spec is None or not isinstance(spec, dict):
        errors.append(f"{kind} 'spec' must be a dictionary.")
        return errors

    if kind == "ResourceClaimTemplate":
        claim_spec = spec.get("spec")
        if not isinstance(claim_spec, dict):
            errors.append("ResourceClaimTemplate 'spec.spec' must be a dictionary.")
            return errors
        devices = claim_spec.get("devices")
        if not isinstance(devices, dict):
            errors.append("ResourceClaimTemplate 'spec.spec.devices' must be a dictionary.")
            return errors
        requests = devices.get("requests")
        if not isinstance(requests, list) or len(requests) == 0:
            errors.append(
                "ResourceClaimTemplate 'spec.spec.devices.requests' must be a non-empty list."
            )
        else:
            for idx, req in enumerate(requests):
                if not isinstance(req, dict):
                    errors.append(
                        f"Request at index {idx} in devices.requests must be a dictionary."
                    )
                    continue
                req_name = req.get("name")
                if not req_name or not isinstance(req_name, str) or not req_name.strip():
                    errors.append(f"Request at index {idx} missing required string 'name'.")
                device_class = req.get("deviceClassName")
                selectors = req.get("selectors")
                if not device_class and not selectors:
                    errors.append(
                        f"Request '{req_name or idx}' in devices.requests must define 'deviceClassName' or 'selectors'."
                    )

    elif kind == "ResourceClaim":
        devices = spec.get("devices")
        if not isinstance(devices, dict):
            errors.append("ResourceClaim 'spec.devices' must be a dictionary.")
            return errors
        requests = devices.get("requests")
        if not isinstance(requests, list) or len(requests) == 0:
            errors.append("ResourceClaim 'spec.devices.requests' must be a non-empty list.")
        else:
            for idx, req in enumerate(requests):
                if not isinstance(req, dict):
                    errors.append(f"Request at index {idx} must be a dictionary.")
                    continue
                req_name = req.get("name")
                if not req_name or not isinstance(req_name, str) or not req_name.strip():
                    errors.append(f"Request at index {idx} missing required string 'name'.")
                if "deviceClassName" not in req and "selectors" not in req:
                    errors.append(
                        f"Request '{req_name or idx}' must define 'deviceClassName' or 'selectors'."
                    )

    elif kind == "DeviceClass":
        if not isinstance(spec, dict):
            errors.append("DeviceClass 'spec' must be a dictionary.")

    else:
        errors.append(f"Unknown DRA kind '{kind}'.")

    return errors


def _validate_hardware_acceleration(
    manifest: Dict[str, Any], exercise_name: Optional[str] = None
) -> List[str]:
    """Validate hardware acceleration configurations (MIG, Apple Silicon MPS, DRA, vLLM)."""
    errors: List[str] = []
    kind = manifest.get("kind", "")

    # Extract pod spec based on kind
    pod_spec: Optional[Dict[str, Any]] = None
    if kind == "Pod":
        pod_spec = manifest.get("spec") if isinstance(manifest.get("spec"), dict) else None
    elif kind in ("Deployment", "StatefulSet", "DaemonSet", "Job"):
        spec = manifest.get("spec")
        if isinstance(spec, dict):
            template = spec.get("template")
            if isinstance(template, dict):
                template_spec = template.get("spec")
                if isinstance(template_spec, dict):
                    pod_spec = template_spec

    if pod_spec is None:
        if exercise_name in ("accel01", "accel02", "accel03", "accel04"):
            errors.append(f"Exercise {exercise_name} requires a valid Pod or workload manifest.")
        return errors

    containers = pod_spec.get("containers", [])
    node_selector = pod_spec.get("nodeSelector", {})
    if node_selector is None or not isinstance(node_selector, dict):
        node_selector = {}

    # General check: GPU / MIG resource limits vs requests consistency across all containers
    if isinstance(containers, list):
        for idx, c in enumerate(containers):
            if not isinstance(c, dict):
                continue
            c_name = c.get("name", f"container[{idx}]")
            resources = c.get("resources", {})
            if isinstance(resources, dict):
                limits = resources.get("limits", {})
                requests = resources.get("requests", {})
                if isinstance(limits, dict) and isinstance(requests, dict):
                    all_keys = set(limits.keys()) | set(requests.keys())
                    for k in all_keys:
                        if (
                            "nvidia.com/mig-" in str(k)
                            or str(k) == "nvidia.com/gpu"
                            or str(k) == "apple.com/gpu"
                        ):
                            if k in limits and k in requests:
                                if str(limits[k]) != str(requests[k]):
                                    errors.append(
                                        f"Container '{c_name}' resource '{k}' limit ({limits[k]}) "
                                        f"and request ({requests[k]}) must match."
                                    )
                            elif any("nvidia.com/mig-" in str(lk) for lk in limits) and any(
                                "nvidia.com/mig-" in str(rk) for rk in requests
                            ):
                                errors.append(
                                    f"Container '{c_name}' NVIDIA MIG resource mismatch between limits and requests."
                                )

    # Exercise-specific checks
    if exercise_name == "accel01":
        if not any("nvidia.com/gpu.product" in str(k) for k in node_selector.keys()):
            errors.append(
                "Exercise accel01 requires 'spec.nodeSelector' with 'nvidia.com/gpu.product'."
            )

        has_mig_resource = False
        has_visible_devices_env = False

        if isinstance(containers, list):
            for c in containers:
                if not isinstance(c, dict):
                    continue
                resources = c.get("resources", {})
                if isinstance(resources, dict):
                    limits = resources.get("limits", {})
                    requests = resources.get("requests", {})
                    if isinstance(limits, dict) and any(
                        "nvidia.com/mig-" in str(k) for k in limits
                    ):
                        has_mig_resource = True
                    if isinstance(requests, dict) and any(
                        "nvidia.com/mig-" in str(k) for k in requests
                    ):
                        has_mig_resource = True

                env = c.get("env", [])
                if isinstance(env, list):
                    for env_var in env:
                        if (
                            isinstance(env_var, dict)
                            and env_var.get("name") == "NVIDIA_VISIBLE_DEVICES"
                        ):
                            has_visible_devices_env = True

        if not has_mig_resource:
            errors.append(
                "Exercise accel01 requires container requesting NVIDIA MIG slice (e.g. nvidia.com/mig-3g.40gb)."
            )
        if not has_visible_devices_env:
            errors.append(
                "Exercise accel01 requires container env variable 'NVIDIA_VISIBLE_DEVICES'."
            )

    elif exercise_name == "accel02":
        if node_selector.get("kubernetes.io/arch") != "arm64":
            errors.append(
                "Exercise accel02 requires 'spec.nodeSelector' with 'kubernetes.io/arch: arm64'."
            )

        has_apple_gpu = False
        has_mps_fallback = False

        if isinstance(containers, list):
            for c in containers:
                if not isinstance(c, dict):
                    continue
                resources = c.get("resources", {})
                if isinstance(resources, dict):
                    limits = resources.get("limits", {})
                    requests = resources.get("requests", {})
                    if isinstance(limits, dict) and "apple.com/gpu" in limits:
                        has_apple_gpu = True
                    if isinstance(requests, dict) and "apple.com/gpu" in requests:
                        has_apple_gpu = True

                env = c.get("env", [])
                if isinstance(env, list):
                    for env_var in env:
                        if isinstance(env_var, dict):
                            if (
                                env_var.get("name") == "PYTORCH_ENABLE_MPS_FALLBACK"
                                and str(env_var.get("value")) == "1"
                            ):
                                has_mps_fallback = True

        if not has_apple_gpu:
            errors.append(
                "Exercise accel02 requires container requesting resource 'apple.com/gpu'."
            )
        if not has_mps_fallback:
            errors.append(
                "Exercise accel02 requires container env variable 'PYTORCH_ENABLE_MPS_FALLBACK: \"1\"'."
            )

    elif exercise_name == "accel03":
        resource_claims = pod_spec.get("resourceClaims")
        if not isinstance(resource_claims, list) or len(resource_claims) == 0:
            errors.append("Exercise accel03 Pod requires non-empty 'spec.resourceClaims'.")
        else:
            claim_names = set()
            for idx, rc in enumerate(resource_claims):
                if not isinstance(rc, dict):
                    errors.append(
                        f"Resource claim at index {idx} in spec.resourceClaims must be a dictionary."
                    )
                    continue
                rc_name = rc.get("name")
                if not rc_name or not isinstance(rc_name, str) or not rc_name.strip():
                    errors.append(f"Resource claim at index {idx} missing required string 'name'.")
                else:
                    claim_names.add(rc_name)
                if not rc.get("resourceClaimTemplateName") and not rc.get("resourceClaimName"):
                    errors.append(
                        f"Resource claim '{rc_name or idx}' must define 'resourceClaimTemplateName' or 'resourceClaimName'."
                    )

            has_claimed_container = False
            if isinstance(containers, list):
                for c in containers:
                    if not isinstance(c, dict):
                        continue
                    c_resources = c.get("resources", {})
                    if isinstance(c_resources, dict):
                        c_claims = c_resources.get("claims")
                        if isinstance(c_claims, list) and len(c_claims) > 0:
                            for cc in c_claims:
                                if isinstance(cc, dict) and cc.get("name") in claim_names:
                                    has_claimed_container = True

            if not has_claimed_container:
                errors.append(
                    "Exercise accel03 requires at least one container referencing a defined claim in 'resources.claims'."
                )

    elif exercise_name == "accel04":
        has_vllm_image = False
        has_gpu_mem_util = False
        has_readiness_probe = False
        has_gpu_resource = False
        has_pvc_volume = False

        volumes = pod_spec.get("volumes", [])
        pvc_volume_names = set()
        if isinstance(volumes, list):
            for v in volumes:
                if isinstance(v, dict) and "persistentVolumeClaim" in v:
                    pvc_info = v.get("persistentVolumeClaim")
                    if isinstance(pvc_info, dict) and pvc_info.get("claimName"):
                        pvc_volume_names.add(v.get("name"))

        if isinstance(containers, list):
            for c in containers:
                if not isinstance(c, dict):
                    continue
                image = str(c.get("image", ""))
                if "vllm" in image or "ollama" in image:
                    has_vllm_image = True

                args = c.get("args", [])
                if isinstance(args, list):
                    args_str = " ".join(str(a) for a in args)
                    if "--gpu-memory-utilization" in args_str:
                        has_gpu_mem_util = True

                resources = c.get("resources", {})
                if isinstance(resources, dict):
                    limits = resources.get("limits", {})
                    requests = resources.get("requests", {})
                    if (isinstance(limits, dict) and any("gpu" in str(k) for k in limits)) or (
                        isinstance(requests, dict) and any("gpu" in str(k) for k in requests)
                    ):
                        has_gpu_resource = True

                readiness_probe = c.get("readinessProbe")
                if isinstance(readiness_probe, dict):
                    if (
                        "httpGet" in readiness_probe
                        or "tcpSocket" in readiness_probe
                        or "exec" in readiness_probe
                    ):
                        has_readiness_probe = True

                volume_mounts = c.get("volumeMounts", [])
                if isinstance(volume_mounts, list):
                    for vm in volume_mounts:
                        if isinstance(vm, dict) and vm.get("name") in pvc_volume_names:
                            has_pvc_volume = True

        if not has_vllm_image:
            errors.append(
                "Exercise accel04 requires a container with a vLLM image (e.g. vllm/vllm-openai)."
            )
        if not has_gpu_mem_util:
            errors.append(
                "Exercise accel04 requires container arg '--gpu-memory-utilization 0.90'."
            )
        if not has_gpu_resource:
            errors.append(
                "Exercise accel04 requires container GPU resource allocation (e.g. nvidia.com/gpu: 1)."
            )
        if not has_readiness_probe:
            errors.append(
                "Exercise accel04 requires container 'readinessProbe' configured (e.g. httpGet /health on port 8000)."
            )
        if not has_pvc_volume:
            errors.append(
                "Exercise accel04 requires a persistentVolumeClaim volume mounted for model cache."
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

    api_version = str(manifest.get("apiVersion", ""))

    # Volcano Job (batch.volcano.sh/v1alpha1)
    if kind == "Job" and ("volcano" in api_version or "batch.volcano.sh" in api_version):
        volcano_errors = _validate_volcano_job(manifest, exercise_name)
        if volcano_errors:
            return False, volcano_errors
        return True, []

    # Volcano Queue (scheduling.volcano.sh/* or batch.volcano.sh/*)
    if kind == "Queue" and ("volcano" in api_version or "scheduling.volcano.sh" in api_version):
        volcano_errors = _validate_volcano_queue(manifest, exercise_name)
        if volcano_errors:
            return False, volcano_errors
        return True, []

    # Kueue validation
    if (
        kind in ("ResourceFlavor", "ClusterQueue", "LocalQueue", "WorkloadPriorityClass")
        or "kueue.x-k8s.io" in api_version
    ):
        kueue_errors = _validate_kueue_resource(manifest, exercise_name)
        if kueue_errors:
            return False, kueue_errors
        return True, []

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

    # DRA validation (resource.k8s.io/*)
    if (
        kind in ("ResourceClaimTemplate", "ResourceClaim", "DeviceClass")
        or "resource.k8s.io" in api_version
    ):
        dra_errors = _validate_dra_resource(manifest, exercise_name)
        if dra_errors:
            return False, dra_errors
        return True, []

    # Standard Kubernetes validation
    try:
        validate_manifest(manifest)
    except ManifestValidationError as e:
        return False, [str(e)]

    if exercise_name == "kueue02" and kind == "Job":
        labels = metadata.get("labels", {})
        if not isinstance(labels, dict) or "kueue.x-k8s.io/queue-name" not in labels:
            return False, [
                "Exercise kueue02 requires Job to have label 'kueue.x-k8s.io/queue-name'."
            ]
        spec = manifest.get("spec", {})
        if isinstance(spec, dict) and spec.get("suspend") is not True:
            return False, [
                "Exercise kueue02 requires Job 'spec.suspend' to be true for Kueue queue gating."
            ]

    # Hardware acceleration validation
    accel_errors = _validate_hardware_acceleration(manifest, exercise_name)
    if accel_errors:
        return False, accel_errors

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
