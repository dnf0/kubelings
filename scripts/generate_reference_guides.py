"""Generate 26 in-depth Kubernetes Reference Guides for MkDocs."""

import json
from pathlib import Path
from kubelings.manifest import get_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO_ROOT / "docs" / "guides"
GUIDES_DIR.mkdir(parents=True, exist_ok=True)

manifest = get_manifest()

CHAPTER_FILENAMES = {
    1: "01-pods.md",
    2: "02-controllers.md",
    3: "03-config-secrets.md",
    4: "04-storage.md",
    5: "05-services-networking.md",
    6: "06-ingress-gateway.md",
    7: "07-scheduling.md",
    8: "08-security-rbac.md",
    9: "09-network-policies.md",
    10: "10-lifecycle-probes.md",
    11: "11-autoscaling.md",
    12: "12-crds-and-operators.md",
    13: "13-troubleshooting.md",
    14: "14-gitops-argocd.md",
    15: "15-service-mesh-cilium.md",
    16: "16-policy-as-code.md",
    17: "17-multitenancy-vcluster.md",
    18: "18-admission-webhooks.md",
    19: "19-helm-packaging.md",
    20: "20-kustomize-overlays.md",
    21: "21-gateway-api.md",
    22: "22-crossplane-iac.md",
    23: "23-ebpf-tetragon.md",
    24: "24-kuberay-ml.md",
    25: "25-batch-kueue-volcano.md",
    26: "26-hardware-acceleration-dra.md",
}

for chapter in manifest.chapters:
    filename = CHAPTER_FILENAMES.get(chapter.number, f"{chapter.number:02d}-{chapter.name}.md")
    guide_path = GUIDES_DIR / filename

    ex_links = []
    for ex in chapter.exercises:
        ex_links.append(f"- [**`{ex.name}`**: {ex.title}](../playground/index.html?exercise={ex.name})")

    exercise_list_md = "\n".join(ex_links)
    
    first_ex = chapter.exercises[0].name if chapter.exercises else "pods01"
    starter_snippet = ""
    if chapter.exercises:
        sol_file = REPO_ROOT / chapter.exercises[0].solution_path
        if sol_file.exists():
            starter_snippet = sol_file.read_text(encoding="utf-8")

    md_content = f"""# Chapter {chapter.number:02d}: {chapter.title}

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; {chapter.description}
-   :material-play-circle: **Interactive Challenges** &bull; {len(chapter.exercises)} Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter={chapter.number}){{ .md-button .md-button--primary }}

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **{chapter.title}** represents fundamental declarative resources managed through continuous control loops. 

```text
    ┌──────────────────────┐          Declarative Manifest (YAML)
    │   kube-apiserver     │ ◄─────────────────────────────────────────────
    └──────────┬───────────┘
               │ (Watches & Stores in etcd)
               ▼
    ┌──────────────────────┐          Reconciles Desired State vs Actual State
    │  Controller / Daemon │ ─────────────────────────────────────────────► [ Cluster State ]
    └──────────────────────┘
```

When you declare resources for this domain, the Kubernetes API Server validates the OpenAPI v3 schema, persists the specification to etcd, and signals the responsible controller or node daemon to reconcile actual state with your desired specification.

---

## 2. Annotated YAML Anatomy & Schema Reference

Below is a production-ready declarative manifest illustrating key fields, structure, and configuration semantics for this chapter:

```yaml
{starter_snippet.strip()}
```

### Key Field Reference

- **`apiVersion`**: The target API group and version for the resource schema.
- **`kind`**: The resource type identifier.
- **`metadata.name`**: Unique DNS-1123 compliant identifier for this resource within its namespace.
- **`metadata.labels`**: Key-value pairs used by selectors, services, and queries.
- **`spec`**: The desired state specification managed by Kubernetes controllers.

---

## 3. Production Best Practices & Hardening Guidelines

1. **Explicit Resource Declarations**: Always specify resource constraints (`requests` and `limits`) to ensure predictable scheduling and prevent node resource starvation.
2. **Immutable Identifiers & Clear Labeling**: Use standard Kubernetes recommended labels (`app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/version`, `app.kubernetes.io/component`).
3. **Defense in Depth**: Follow least-privilege security principles (e.g. `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, dropping all unnecessary Linux capabilities).
4. **Health Check Probes**: Configure comprehensive startup, liveness, and readiness probes with appropriate failure thresholds and timing delays.
5. **Declarative GitOps Management**: Maintain all manifests in version control and deploy through automated reconciliation pipelines.

---

## 4. Troubleshooting & Diagnostic Workflows

When inspecting or debugging resources in this category, use the following triage sequence:

```bash
# 1. Check resource status and conditions
kubectl get {chapter.name.split('_')[-1]} -o wide

# 2. Inspect detailed control plane events and controller messages
kubectl describe {chapter.name.split('_')[-1]} <resource-name>

# 3. Stream real-time logs (if applicable)
kubectl logs -l app=<label> --tail=100 -f
```

---

## 5. Interactive Practice Exercises

Practice the concepts from this chapter directly in your browser using our client-side WebAssembly environment:

{exercise_list_md}

<div style="margin-top: 1.5rem;">
  <a href="../playground/index.html?chapter={chapter.number}" class="md-button md-button--primary">
    ⚡ Practice Chapter {chapter.number:02d} in WebAssembly Playground →
  </a>
</div>
"""
    guide_path.write_text(md_content.strip() + "\n", encoding="utf-8")
    print(f"✓ Generated {guide_path.relative_to(REPO_ROOT)}")

print(f"\nAll 26 reference guides successfully generated in {GUIDES_DIR.relative_to(REPO_ROOT)}")
