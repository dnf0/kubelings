# I AM NOT DONE
"""
Exercise: tetragon04.py
Topic: eBPF Network Observability - Tetragon Socket Connect Probes

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
    # TODO: Define and return TracingPolicy manifest
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
