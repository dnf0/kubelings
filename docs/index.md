# Kubelings ☸️

**An interactive, hands-on CLI learning environment for Kubernetes.**

Inspired by [rustlings](https://github.com/rust-lang/rustlings), [ziglings](https://github.com/ziglings/exercises), and [raylings](https://github.com/ray-project/raylings), **Kubelings** guides engineers through self-paced micro-exercises directly in the terminal.

---

## Why Kubelings?

Learning Kubernetes from static documentation or copy-pasted manifests often leads to frustration because error feedback is slow and cryptic. Kubelings provides:

- ⚡ **Sub-30ms Instant Feedback**: In-memory schema and spec validation without waiting on slow API servers.
- 🔁 **Active Problem Solving**: 70 real-world exercises starting in a broken state that you fix and verify.
- ☸ **Dual-Mode Engine**: Practice 100% offline or connect to a real cluster (`kind`, `minikube`, `k3d`, or cloud).
- 💡 **Progressive Hinting**: Multi-tier clues when you get stuck without spoiling the answer.
- 🚀 **Zero-Install Run**: Start practicing immediately with `uvx kubelings init && uvx kubelings watch`.

---

## Quick Example

```python
# exercises/01_pods/pods01.py
# I AM NOT DONE

from typing import Any, Dict

def get_pod_manifest() -> Dict[str, Any]:
    # Fix the pod manifest specification
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "nginx-web"},
        "spec": {
            "containers": [
                {"name": "nginx", "image": "nginx:alpine", "ports": [{"containerPort": 80}]}
            ]
        },
    }
```

Remove the `# I AM NOT DONE` marker, save the file, and watch the terminal UI advance to the next exercise automatically!
