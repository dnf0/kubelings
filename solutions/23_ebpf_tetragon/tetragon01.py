"""
Solution: tetragon01.py
Topic: eBPF Observability - Tetragon TracingPolicy Process Execution Auditing
"""


def build_tracing_policy() -> dict:
    return {
        "apiVersion": "cilium.io/v1alpha1",
        "kind": "TracingPolicy",
        "metadata": {
            "name": "audit-process-execution",
        },
        "spec": {
            "kprobes": [
                {
                    "call": "sys_execve",
                    "syscall": True,
                    "args": [
                        {
                            "index": 0,
                            "type": "string",
                        },
                    ],
                    "selectors": [
                        {
                            "matchNamespaces": [
                                {
                                    "operator": "In",
                                    "values": ["production", "payments"],
                                },
                            ],
                            "matchArgs": [
                                {
                                    "index": 0,
                                    "operator": "Prefix",
                                    "values": ["/bin/", "/usr/bin/"],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    }


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
