"""
Exercise: tetragon01.py
Topic: eBPF Observability - Tetragon TracingPolicy Process Execution Auditing

Context & Why:
Cilium Tetragon is an eBPF-based security observability and runtime enforcement platform.
Traditional Linux security auditing tools (like auditd) operate in user space with significant
performance overhead, high CPU consumption, and vulnerability to event dropping under heavy load.

Tetragon attaches eBPF kernel probes (kprobes) directly inside the Linux kernel:
- Intercepts system calls (such as `sys_execve`) at the exact moment a process binary is executed.
- Enriches low-level kernel events with rich Kubernetes context (namespace, pod name, container ID)
  via eBPF maps before events leave the kernel.
- In-kernel filtering with selectors (`matchNamespaces`, `matchArgs`) ensures only events matching
  critical criteria (e.g., binaries executed under `/bin/` or `/usr/bin/` in production namespaces)
  generate telemetry, drastically reducing noise and event processing overhead.

Task:
Define an eBPF TracingPolicy to monitor container process execution in real time:
1. 'apiVersion': 'cilium.io/v1alpha1', 'kind': 'TracingPolicy'
2. Named 'audit-process-execution'
3. 'spec.kprobes': Define 1 kernel probe:
   - 'call': 'sys_execve'
   - 'syscall': True
   - 'args': [{'index': 0, 'type': 'string'}] (captures binary path)
   - 'selectors':
     * 'matchNamespaces': [{'operator': 'In', 'values': ['production', 'payments']}]
     * 'matchArgs': [{'index': 0, 'operator': 'Prefix', 'values': ['/bin/', '/usr/bin/']}]
"""

import yaml


def build_tracing_policy() -> dict:
    # TODO: Define and return the Tetragon TracingPolicy manifest monitoring sys_execve kprobes across production namespaces.
    # WHY: eBPF-based kernel tracing captures process execution at the syscall level before userland execution occurs,
    #      providing high-fidelity runtime security auditing without the latency or vulnerability to evasion found in user-space agents.
    return {}


def verify():
    policy = build_tracing_policy()
    assert policy.get("apiVersion") in ["cilium.io/v1alpha1", "cilium.io/v1"]
    assert policy.get("kind") == "TracingPolicy"
    assert policy.get("metadata", {}).get("name") == "audit-process-execution"

    kprobes = policy.get("spec", {}).get("kprobes", [])
    assert len(kprobes) == 1, f"Expected 1 kprobe, found {len(kprobes)}"
    kp = kprobes[0]
    assert kp.get("call") == "sys_execve"
    assert kp.get("syscall") is True

    args = kp.get("args", [])
    assert len(args) == 1
    assert args[0].get("index") == 0 and args[0].get("type") == "string"

    selectors = kp.get("selectors", [])
    assert len(selectors) == 1
    sel = selectors[0]

    ns = sel.get("matchNamespaces", [])[0]
    assert ns.get("operator") == "In"
    assert "production" in ns.get("values", []) and "payments" in ns.get("values", [])

    margs = sel.get("matchArgs", [])[0]
    assert margs.get("index") == 0
    assert margs.get("operator") == "Prefix"
    assert "/bin/" in margs.get("values", []) and "/usr/bin/" in margs.get("values", [])

    print("✓ Tetragon eBPF Process Execution TracingPolicy successfully validated!")


if __name__ == "__main__":
    verify()
