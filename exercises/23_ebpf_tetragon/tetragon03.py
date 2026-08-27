# I AM NOT DONE
"""
Exercise: tetragon03.py
Topic: eBPF Security - Real-Time Kernel Enforcement and Sigkill Actions

Task:
Define a Tetragon TracingPolicy that actively blocks unauthorized privilege escalation binaries by sending Sigkill:
1. 'apiVersion': 'cilium.io/v1alpha1', 'kind': 'TracingPolicy'
2. Named 'block-privilege-escalation'
3. 'spec.kprobes': Define 1 kernel probe:
   - 'call': 'sys_execve'
   - 'syscall': True
   - 'args': [{'index': 0, 'type': 'string'}]
   - 'selectors':
     * 'matchArgs': [
         {
           'index': 0,
           'operator': 'Exact',
           'values': ['/usr/bin/sudo', '/usr/bin/su', '/usr/bin/nsenter']
         }
       ]
     * 'matchActions': [{'action': 'Sigkill'}]
"""

import yaml


def build_enforcement_policy() -> dict:
    # TODO: Define and return TracingPolicy manifest
    return {}


def verify():
    policy = build_enforcement_policy()
    assert policy.get("apiVersion") in ["cilium.io/v1alpha1", "cilium.io/v1"]
    assert policy.get("kind") == "TracingPolicy"
    assert policy.get("metadata", {}).get("name") == "block-privilege-escalation"

    kprobes = policy.get("spec", {}).get("kprobes", [])
    assert len(kprobes) == 1
    kp = kprobes[0]
    assert kp.get("call") == "sys_execve"

    sel = kp.get("selectors", [])[0]
    margs = sel.get("matchArgs", [])[0]
    assert margs.get("index") == 0
    assert margs.get("operator") == "Exact"
    assert "/usr/bin/sudo" in margs.get("values", [])
    assert "/usr/bin/nsenter" in margs.get("values", [])

    actions = sel.get("matchActions", [])
    assert len(actions) == 1
    assert actions[0].get("action") == "Sigkill"

    print("✓ Tetragon eBPF Kernel Sigkill Enforcement Policy successfully validated!")


if __name__ == "__main__":
    verify()
