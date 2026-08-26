# Kubelings: An Interactive Hands-On Kubernetes Learning Environment

**Date:** 2026-08-26  
**Status:** Approved  
**Target Repository:** `dnf0/kubelings`  

---

## 1. Executive Summary & Vision

`kubelings` is an interactive, terminal-driven educational tool and comprehensive curriculum designed to teach Kubernetes from foundational building blocks to production cloud-native engineering—inspired by the pedagogy and developer experience of `rustlings`, `ziglings`, and `raylings`.

Learners progress through hands-on, self-guided exercises where they fix broken YAML manifests, construct multi-container sidecars, configure persistent storage, write RBAC security policies, solve scheduling constraints, build custom Python Kubernetes operators, and troubleshoot production cluster incidents (such as `CrashLoopBackOff`, OOMKilled containers, and scheduling deadlocks).

---

## 2. System Architecture

```
                                +-----------------------------+
                                |      Learner Terminal       |
                                |       kubelings watch       |
                                +--------------+--------------+
                                               |
                                               v
+------------------------------------------------------------------------------------------+
|                                  Kubelings CLI Engine                                    |
|                                                                                          |
|  +--------------------+   +-----------------------+   +-------------------------------+  |
|  | File Watcher       |   | Progress / State Mgr  |   | Exercise Runner & Validator   |  |
|  | (watchfiles)       |-->| (exercise index &     |-->| (syntax check, test eval,     |  |
|  |                    |   |  marker parser)       |   |  manifest schema & assertion) |  |
|  +--------------------+   +-----------------------+   +---------------+---------------+  |
|                                                                       |                  |
+-----------------------------------------------------------------------|------------------+
                                                                        |
                                       +--------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------------------+
|                               Kubernetes Validation Layer                                |
|                                                                                          |
|  +---------------------------------------------+  +-----------------------------------+  |
|  | Fast In-Memory Schema & Mock API Engine     |  | Live Cluster Adapter (Optional)   |  |
|  | - Sub-30ms offline schema validation        |  | - Direct kind/minikube/k3s check  |  |
|  | - OpenAPI models & YAML structure parser    |  | - Namespace isolation & cleanup   |  |
|  | - Pure Python Kubernetes client testing     |  | - Live resource lifecycle check   |  |
|  +---------------------------------------------+  +-----------------------------------+  |
|                                                                                          |
+------------------------------------------------------------------------------------------+
```

### 2.1 Core Components

1. **CLI Engine (`kubelings/cli.py`, `kubelings/runner.py`, `kubelings/watcher.py`, `kubelings/ui.py`)**:
   - Built on `typer` and `rich`.
   - Manages interactive command modes (`watch`, `run`, `test`, `hint`, `list`, `verify`).
   - Renders clean, color-coded terminal diagnostics, stack traces, progress bars, and victory ASCII banners.

2. **Schema & Manifest Validator (`kubelings/validator.py`)**:
   - Validates Kubernetes YAML manifests and Python Kubernetes client data objects against standard Kubernetes OpenAPI v3 schemas.
   - Provides sub-30ms instant feedback without requiring a live cluster for schema and configuration exercises.

3. **Cluster Adapter & Runtime (`kubelings/cluster.py`)**:
   - Detects active kubeconfig contexts (`kind`, `minikube`, `k3d`, or cloud clusters).
   - Provides optional live reconciliation checking for exercises involving real cluster resource deployment and verification.
   - Automatically provisions and cleans up ephemeral test namespaces (`kubelings-test-*`) to prevent cluster pollution.

4. **Exercise Manifest & Registry (`kubelings/manifest.py`, `kubelings/models.py`)**:
   - Declarative catalogue of all 13 chapters and 55 exercises with titles, paths, prerequisites, and progressive hints.
   - Parses `# I AM NOT DONE` marker at the top of exercise files.

5. **Canonical Solutions & Testing Harness (`solutions/`, `tests/`)**:
   - `solutions/` mirrors every exercise file in `exercises/` with verified reference implementations.
   - Pytest test suite validates that:
     - All solutions pass verification.
     - All starter exercises in `exercises/` fail before the user fixes them (preventing accidental no-op exercises).
     - CLI commands, runner, and watcher logic execute properly.

---

## 3. Curriculum & Syllabus Specification

The curriculum consists of 13 chapters spanning 55 focused exercises:

### Chapter 1: Kubernetes Core Workloads & Pods (`01_pods`)
- `exercises/01_pods/pods01.py`: First Pod manifest & API structure (metadata, spec, containers, ports).
- `exercises/01_pods/pods02.py`: Multi-container Pods & Sidecar pattern (shared volumes, IPC communication).
- `exercises/01_pods/pods03.py`: Init Containers for dependency ordering and initialization scripts.
- `exercises/01_pods/pods04.py`: Pod resource requests, limits, and QoS classes (Guaranteed, Burstable, BestEffort).
- `exercises/01_pods/pods05.py`: Environment variables & Downward API (`fieldRef`, `resourceFieldRef`).
- `exercises/01_pods/pods06.py`: Static Pods vs API-managed Pods & Pod Disruption Budgets (PDB).

### Chapter 2: Controllers & Replication (`02_controllers`)
- `exercises/02_controllers/ctrl01.py`: ReplicaSets and label selector matching (`matchLabels`, `matchExpressions`).
- `exercises/02_controllers/ctrl02.py`: Deployments: RollingUpdate vs Recreate strategies and `maxSurge`/`maxUnavailable`.
- `exercises/02_controllers/ctrl03.py`: Deployment rollbacks, revision history, and undoing broken releases.
- `exercises/02_controllers/ctrl04.py`: StatefulSets: Stable network IDs, headless services, and ordinal indexing.
- `exercises/02_controllers/ctrl05.py`: DaemonSets: Running node-level daemons and nodeSelector/tolerations.
- `exercises/02_controllers/ctrl06.py`: Jobs and CronJobs: Backoff limits, completions, parallelism, and schedule syntax.

### Chapter 3: Configuration & Secret Management (`03_config_secrets`)
- `exercises/03_config_secrets/config01.py`: ConfigMaps from literals and files; mounting as env vars (`envFrom`, `valueFrom`).
- `exercises/03_config_secrets/config02.py`: ConfigMaps mounted as volume files; live reload semantics and subPaths.
- `exercises/03_config_secrets/config03.py`: Secrets: Base64 encoding, opaque secrets, and TLS certificates.
- `exercises/03_config_secrets/config04.py`: Secret volume mounts, memory-backed tmpfs storage, and read-only permissions.
- `exercises/03_config_secrets/config05.py`: Immutable ConfigMaps and Secrets for performance and drift prevention.

### Chapter 4: Storage & Persistent Volumes (`04_storage`)
- `exercises/04_storage/storage01.py`: `emptyDir` and `hostPath` volume types.
- `exercises/04_storage/storage02.py`: PersistentVolumes (PV) & PersistentVolumeClaims (PVC) binding mechanics.
- `exercises/04_storage/storage03.py`: AccessModes (`ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`) and reclaim policies (`Retain`, `Delete`).
- `exercises/04_storage/storage04.py`: StorageClasses & dynamic volume provisioning (`volumeBindingMode: WaitForFirstConsumer`).
- `exercises/04_storage/storage05.py`: Volume snapshots and volume expansion (`allowVolumeExpansion`).

### Chapter 5: Services & Networking (`05_services_networking`)
- `exercises/05_services_networking/net01.py`: ClusterIP Services: Port mapping (`port`, `targetPort`), endpoints, and selector matching.
- `exercises/05_services_networking/net02.py`: Headless Services (`clusterIP: None`) for StatefulSet direct addressing & SRV records.
- `exercises/05_services_networking/net03.py`: NodePort and LoadBalancer service types.
- `exercises/05_services_networking/net04.py`: CoreDNS internal resolution (`<service>.<namespace>.svc.cluster.local`) and search paths.
- `exercises/05_services_networking/net05.py`: ExternalName services and manual Endpoints / EndpointSlices.

### Chapter 6: Ingress & Gateway API (`06_ingress_gateway`)
- `exercises/06_ingress_gateway/ingress01.py`: Ingress resource definitions: host-based and path-based routing rules.
- `exercises/06_ingress_gateway/ingress02.py`: Ingress TLS termination with Secret certificates.
- `exercises/06_ingress_gateway/ingress03.py`: Ingress rewrite-target annotations and custom headers.
- `exercises/06_ingress_gateway/ingress04.py`: Gateway API fundamentals: `GatewayClass`, `Gateway`, and `HTTPRoute`.

### Chapter 7: Scheduling, Affinity & Advanced Placement (`07_scheduling`)
- `exercises/07_scheduling/sched01.py`: Manual node assignment (`nodeName`) and simple `nodeSelector`.
- `exercises/07_scheduling/sched02.py`: Node Affinity: `requiredDuringSchedulingIgnoredDuringExecution` vs `preferred...`.
- `exercises/07_scheduling/sched03.py`: Pod Affinity & Pod Anti-Affinity: Spreading pods across topology keys.
- `exercises/07_scheduling/sched04.py`: Taints and Tolerations: Dedicated nodes, `NoSchedule`, `NoExecute`, and eviction delays.
- `exercises/07_scheduling/sched05.py`: Topology Spread Constraints: `maxSkew` and `whenUnsatisfiable`.

### Chapter 8: Security, RBAC & Service Accounts (`08_security_rbac`)
- `exercises/08_security_rbac/rbac01.py`: ServiceAccounts and automounting service account tokens.
- `exercises/08_security_rbac/rbac02.py`: Roles & RoleBindings (namespace-scoped permissions: verbs, apiGroups, resources).
- `exercises/08_security_rbac/rbac03.py`: ClusterRoles & ClusterRoleBindings (cluster-wide access and non-resource URLs).
- `exercises/08_security_rbac/rbac04.py`: SecurityContext: `runAsUser`, `runAsNonRoot`, `readOnlyRootFilesystem`, `capabilities`.
- `exercises/08_security_rbac/rbac05.py`: Pod Security Standards (Privileged, Baseline, Restricted) via namespace labels.

### Chapter 9: Network Policies & Traffic Segmentation (`09_network_policies`)
- `exercises/09_network_policies/netpol01.py`: Default Deny all ingress & egress network policy.
- `exercises/09_network_policies/netpol02.py`: Ingress traffic filtering by podSelector and namespaceSelector.
- `exercises/09_network_policies/netpol03.py`: Egress traffic filtering (allowing DNS port 53 while blocking external CIDRs).
- `exercises/09_network_policies/netpol04.py`: Named ports and IPBlock CIDR exception rules in NetworkPolicies.

### Chapter 10: Health Checking, Probes & Lifecycle (`10_lifecycle_probes`)
- `exercises/10_lifecycle_probes/health01.py`: Liveness probes (HTTP, TCP socket, Exec command) & restart triggers.
- `exercises/10_lifecycle_probes/health02.py`: Readiness probes and automatic traffic gating in Service endpoints.
- `exercises/10_lifecycle_probes/health03.py`: Startup probes for slow-starting applications.
- `exercises/10_lifecycle_probes/health04.py`: Container lifecycle hooks (`postStart`, `preStop`) and graceful termination (`terminationGracePeriodSeconds`).

### Chapter 11: Autoscaling (HPA, VPA, KEDA) (`11_autoscaling`)
- `exercises/11_autoscaling/autoscale01.py`: HorizontalPodAutoscaler (HPA v2) based on target CPU/Memory utilization.
- `exercises/11_autoscaling/autoscale02.py`: HPA custom behavior policies: scale-up and scale-down stabilization windows.
- `exercises/11_autoscaling/autoscale03.py`: VerticalPodAutoscaler (VPA): `recommendationMode`, auto-resizing pods.
- `exercises/11_autoscaling/autoscale04.py`: Event-driven autoscaling concepts (KEDA ScaledObjects / external metrics).

### Chapter 12: Custom Resources, CRDs & Operators (`12_crds_and_operators`)
- `exercises/12_crds_and_operators/crd01.py`: CustomResourceDefinition (CRD) schema specification with OpenAPI v3 validation.
- `exercises/12_crds_and_operators/crd02.py`: Subresources (`/status` and `/scale`) and printer columns in CRDs.
- `exercises/12_crds_and_operators/crd03.py`: Building a Python Kubernetes Operator reconciliation loop.
- `exercises/12_crds_and_operators/crd04.py`: Dynamic admission webhooks (Mutating & Validating webhooks).

### Chapter 13: Observability, Debugging & Production Troubleshooting (`13_troubleshooting`)
- `exercises/13_troubleshooting/troubleshoot01.py`: Debugging `CrashLoopBackOff`, exit codes (137 OOMKilled, 1, 143), and container logs.
- `exercises/13_troubleshooting/troubleshoot02.py`: Debugging `ImagePullBackOff` and `ErrImagePull` (registry auth, tags).
- `exercises/13_troubleshooting/troubleshoot03.py`: Debugging `Pending` pods (insufficient resources, affinity mismatch, unattached PVCs).
- `exercises/13_troubleshooting/troubleshoot04.py`: ResourceQuotas and LimitRanges: resolving quota exceeded rejections.
- `exercises/13_troubleshooting/troubleshoot05.py`: Ephemeral debug containers (`kubectl debug`) and cluster event triage.

---

## 4. Exercise & Solution File Structure

Every exercise file follows a clean, consistent convention:

```python
"""
Exercise: exercises/01_pods/pods01.py
Topic: First Pod Manifest & Container Specification

Instructions:
Fix the YAML manifest below to define a valid Pod named 'nginx-web'
running nginx:alpine on container port 80 with label 'app: web'.
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: ???
  labels:
    app: ???
spec:
  containers:
  - name: nginx
    image: ???
    ports:
    - containerPort: 80
"""

def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod")
    
    assert manifest["metadata"]["name"] == "nginx-web", "Pod name must be 'nginx-web'"
    assert manifest["metadata"]["labels"]["app"] == "web", "Label 'app' must equal 'web'"
    container = manifest["spec"]["containers"][0]
    assert container["image"] == "nginx:alpine", "Container image must be 'nginx:alpine'"
    assert container["ports"][0]["containerPort"] == 80, "Port must be 80"
    print("✓ pods01 passed!")

if __name__ == "__main__":
    verify()
```

---

## 5. Repository Infrastructure & CI

### 5.1 Packaging & Environment (`pyproject.toml`)
- Build Backend: `hatchling`
- Entry Point: `[project.scripts] kubelings = "kubelings.cli:app"`
- Package Manager: `uv`
- Python Version: `>=3.10`
- Core Dependencies:
  - `kubernetes>=29.0.0`
  - `pyyaml>=6.0.1`
  - `pydantic>=2.6.0`
  - `jsonschema>=4.20.0`
  - `rich>=13.7.0`
  - `typer>=0.12.0`
  - `watchfiles>=0.21.0`
- Dev Dependencies:
  - `pytest>=8.0.0`
  - `pytest-cov>=4.1.0`
  - `ruff>=0.4.0`
  - `pyright>=1.1.350`
  - `pre-commit>=3.7.0`

### 5.2 Agent Rules & Git Isolation
- Standard `.gitignore` excluding all agent-internal paths (`.agents/`, `.agent-state/`, `.superpowers/`, `graphify-out/`, `.roborev/`, `.claude/`, `.gemini/`) from commits, keeping `dnf0/kubelings` ready for public open-source publication.

### 5.3 Automated CI Workflow (`.github/workflows/ci.yml`)
- Triggers on push to `main` and pull requests.
- Matrix runs on Python `3.10`, `3.11`, `3.12`.
- Execution Steps:
  1. `uv sync` dependencies.
  2. `ruff check` and `ruff format --check`.
  3. `pyright` type checks on `src/kubelings/` and `solutions/`.
  4. `pytest tests/` verifying that:
     - All solutions in `solutions/` pass verification.
     - All starter exercises in `exercises/` fail as expected.
     - CLI commands and watcher logic pass unit tests.

---

## 6. Verification and Acceptance Criteria

1. **CLI Commands**:
   - `kubelings watch` automatically discovers incomplete exercises, monitors edits, re-evaluates in <50ms, and updates live status.
   - `kubelings run <path>` runs any exercise or solution.
   - `kubelings hint` reveals progressive hints per exercise.
   - `kubelings test` verifies all reference solutions.
   - `kubelings list` outputs the complete curriculum table with statuses.
2. **Curriculum Completeness**:
   - 13 chapters, 55 deep-dive exercises with verified matching solutions.
3. **CI & Code Quality**:
   - 100% passing test suite on Python 3.10+.
   - Clean linting (`ruff`) and static typing (`pyright`).
4. **GitHub Deployment Ready**:
   - Remote target: `git@github.com:dnf0/kubelings.git`.
