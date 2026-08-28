"""
Exercise: tetragon04.py
Topic: eBPF Network Observability - Tetragon Socket Connect Probes

Context & Why:
Deep visibility into outbound network connections is essential for identifying command-and-control (C2)
beaconing, data exfiltration, and unauthorized lateral movement between microservices.

Instead of intercepting packets at the network interface layer (which incurs packet capture overhead),
Tetragon hooks internal kernel networking functions such as `tcp_connect`:
- Hooks the non-syscall kernel function `tcp_connect` (`syscall: False`) with argument type `sock`.
- Extracts destination IP, destination port, and source socket details directly from kernel `struct sock`.
- Correlates socket establishment events with Kubernetes pod and namespace metadata.
- Emits structured events via `matchActions: [{action: 'Post'}]` to the Tetragon gRPC stream, enabling
  real-time SIEM ingestion without modifying application code or container sidecars.

Task:
Define a TracingPolicy monitoring network socket connections (`tcp_connect`):
1. 'apiVersion': 'cilium.io/v1alpha1', 'kind': 'TracingPolicy'
2. Named 'trace-outbound-tcp-connections'
3. 'spec.kprobes': Define 1 kernel probe:
   - 'call': 'tcp_connect'
   - 'syscall': False
   - 'args': [{'index': 0, 'type': 'sock'}]
   - 'selectors':
     * 'matchNamespaces': [{'operator': 'In', 'values': ['backend', 'database']}]
     * 'matchActions': [{'action': 'Post'}] (publishes event to Tetragon gRPC event stream)
"""

import yaml


def build_socket_tracing_policy() -> dict:
    # TODO: Define and return the Tetragon TracingPolicy manifest capturing tcp_connect kernel probes and streaming events via Post actions.
    # WHY: Hooking kernel TCP socket connections provides protocol-agnostic egress visibility into outbound connections and microservice
    #      communication patterns directly at the network stack, identifying C2 beaconing and unauthorized egress.
    return {}


def verify():
    policy = build_socket_tracing_policy()
    assert policy.get("apiVersion") in ["cilium.io/v1alpha1", "cilium.io/v1"]
    assert policy.get("kind") == "TracingPolicy"
    assert policy.get("metadata", {}).get("name") == "trace-outbound-tcp-connections"

    kprobes = policy.get("spec", {}).get("kprobes", [])
    assert len(kprobes) == 1
    kp = kprobes[0]
    assert kp.get("call") == "tcp_connect"
    assert kp.get("syscall") is False

    args = kp.get("args", [])
    assert len(args) == 1
    assert args[0].get("index") == 0 and args[0].get("type") == "sock"

    sel = kp.get("selectors", [])[0]
    ns = sel.get("matchNamespaces", [])[0]
    assert "backend" in ns.get("values", [])
    assert "database" in ns.get("values", [])

    actions = sel.get("matchActions", [])
    assert len(actions) == 1
    assert actions[0].get("action") == "Post"

    print("✓ Tetragon eBPF TCP Socket Observability TracingPolicy successfully validated!")


if __name__ == "__main__":
    verify()
