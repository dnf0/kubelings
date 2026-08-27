# Check Your Environment & Cluster 🌐

Kubelings is engineered with an **offline-first architecture**, meaning you can learn and solve exercises anywhere—even without internet connectivity or a running Kubernetes cluster!

---

### ⚡ Offline-First vs. Live Cluster Modes

- **Offline-First In-Memory Validation (Default)**:
  All standard exercises validate Kubernetes manifests against official OpenAPI schemas, structural constraints, and Python assertion suites in `<30ms` without needing Docker, Minikube, or cloud resources.

- **Live Cluster Mode (Optional & Auto-Detected)**:
  If a local Kubernetes cluster is active (such as **Kind**, **Minikube**, **k3d**, or **Docker Desktop**), Kubelings automatically detects it. Live exercises and controller verification run against your active kubeconfig context.

---

### 🔍 Run Cluster Diagnostics

Click below to test your current Kubernetes context and environment:

[Check Cluster Status](command:kubelings.checkCluster)
