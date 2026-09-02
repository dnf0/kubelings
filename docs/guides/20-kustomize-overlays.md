# Chapter 20: Declarative Customization with Kustomize

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Base Manifests, ConfigMap/Secret Generators, Patches, and Multi-Environment Overlays
-   :material-api: **Primary APIs** &bull; `kustomize.config.k8s.io/v1beta1` &bull; `Kustomization`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=20){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`kustomize01`**: Kustomize Base Manifests & Metadata Transformations →](../playground/index.html?exercise=kustomize01)
    - [**`kustomize02`**: Kustomize ConfigMap & Secret Generators →](../playground/index.html?exercise=kustomize02)
    - [**`kustomize03`**: Kustomize Strategic Merge & JSON6902 Target Patches →](../playground/index.html?exercise=kustomize03)
    - [**`kustomize04`**: Kustomize Multi-Environment Overlays & Image Transforms →](../playground/index.html?exercise=kustomize04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Declarative Customization with Kustomize** is reconciled through declarative state loops managed by the control plane:

```mermaid
flowchart LR
    subgraph BaseLayer["Base Configuration (Dry, Reusable)"]
        BASE_K["base/kustomization.yaml"]
        BASE_RES["base/deployment.yaml<br/>base/service.yaml"]
        BASE_RES --> BASE_K
    end

    subgraph OverlayLayer["Environment Overlays"]
        DEV_K["overlays/dev/kustomization.yaml<br/><i>replicas: 1, debug: true</i>"]
        PROD_K["overlays/prod/kustomization.yaml<br/><i>replicas: 10, namePrefix: prod-</i>"]

        BASE_K --> DEV_K
        BASE_K --> PROD_K
    end

    subgraph BuildEngine["Kustomize Processing Engine"]
        ENGINE["Strategic Merge & JSON 6902 Patch Engine<br/><code>kustomize build overlays/prod</code>"]
        PROD_K --> ENGINE
    end

    subgraph OutputManifests["Target Declarative Manifests"]
        FINAL_YAML["Production Declarative Manifests<br/><i>(Prefixes, Patches, Hash-suffixed ConfigMaps)</i>"]
        ENGINE --> FINAL_YAML
    end
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
namePrefix: prod-
commonLabels:
  environment: production
  managed-by: kustomize
resources:
- ../../base
patches:
- target:
    kind: Deployment
    name: web-app
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 10
configMapGenerator:
- name: app-env
  behavior: merge
  literals:
  - LOG_LEVEL=warn
  - CACHE_TTL=3600
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `resources` | `Array` | Relative paths to bases, other overlays, or remote Git URLs. |
| `patches` | `Array` | Targeted JSON 6902 patches or Strategic Merge Patches modifying specific fields without duplicating manifests. |
| `configMapGenerator` | `Array` | Generates ConfigMaps with automatic content-hash suffixes for zero-downtime rolling updates. |

---

## 3. Real-World Architectural Patterns

### Base Kustomization Definition

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
```

### Strategic Merge Patch for Resource Limits

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```


---

## 4. Production Hardening & Operational Governance

- Use `configMapGenerator` with hash suffixes so configuration updates trigger automated rolling restarts.
- Keep `base/` minimal and purely structural; push environment-specific configurations into `overlays/`.
- Validate Kustomize builds in CI with `kubectl kustomize overlays/production --dry-run=client`.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`patch target not found`"
    **Root Cause:** Patch target `kind` or `name` does not match any resource generated in the base.

    **Diagnostic Triage Sequence:**
    1. Review base build output: `kubectl kustomize base`
    2. Verify `namePrefix` or `nameSuffix` has not modified the target name prior to patching.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`kustomize01`** | Kustomize Base Manifests & Metadata Transformations | [`../playground/index.html?exercise=kustomize01`](../playground/index.html?exercise=kustomize01) | [**⚡ Solve `kustomize01` in Playground →**](../playground/index.html?exercise=kustomize01){ .md-button .md-button--primary } |
| **`kustomize02`** | Kustomize ConfigMap & Secret Generators | [`../playground/index.html?exercise=kustomize02`](../playground/index.html?exercise=kustomize02) | [**⚡ Solve `kustomize02` in Playground →**](../playground/index.html?exercise=kustomize02){ .md-button .md-button--primary } |
| **`kustomize03`** | Kustomize Strategic Merge & JSON6902 Target Patches | [`../playground/index.html?exercise=kustomize03`](../playground/index.html?exercise=kustomize03) | [**⚡ Solve `kustomize03` in Playground →**](../playground/index.html?exercise=kustomize03){ .md-button .md-button--primary } |
| **`kustomize04`** | Kustomize Multi-Environment Overlays & Image Transforms | [`../playground/index.html?exercise=kustomize04`](../playground/index.html?exercise=kustomize04) | [**⚡ Solve `kustomize04` in Playground →**](../playground/index.html?exercise=kustomize04){ .md-button .md-button--primary } |
