"""
Exercise: tetragon02.py
Topic: eBPF Observability - Tetragon File and Token Access Monitoring

Task:
Define a TracingPolicy to monitor access to sensitive files and service account tokens:
1. 'apiVersion': 'cilium.io/v1alpha1', 'kind': 'TracingPolicy'
2. Named 'monitor-sensitive-file-access'
3. 'spec.kprobes': Define 1 kernel probe:
   - 'call': 'sys_openat'
   - 'syscall': True
   - 'args': [
       {'index': 0, 'type': 'int'},
       {'index': 1, 'type': 'string'} (the path parameter)
     ]
   - 'selectors':
     * 'matchArgs': [
         {
           'index': 1,
           'operator': 'Prefix',
           'values': ['/etc/shadow', '/var/run/secrets/kubernetes.io']
         }
       ]
"""

import yaml


def build_file_monitor_policy() -> dict:
    # TODO: Define and return TracingPolicy manifest
    return {}


def verify():
    policy = build_file_monitor_policy()
    assert policy.get("apiVersion") in ["cilium.io/v1alpha1", "cilium.io/v1"]
    assert policy.get("kind") == "TracingPolicy"
    assert policy.get("metadata", {}).get("name") == "monitor-sensitive-file-access"

    kprobes = policy.get("spec", {}).get("kprobes", [])
    assert len(kprobes) == 1
    kp = kprobes[0]
    assert kp.get("call") == "sys_openat"
    assert kp.get("syscall") is True

    args = kp.get("args", [])
    assert len(args) == 2
    assert args[1].get("index") == 1 and args[1].get("type") == "string"

    sel = kp.get("selectors", [])[0]
    margs = sel.get("matchArgs", [])[0]
    assert margs.get("index") == 1
    assert margs.get("operator") == "Prefix"
    assert "/etc/shadow" in margs.get("values", [])
    assert "/var/run/secrets/kubernetes.io" in margs.get("values", [])

    print("✓ Tetragon eBPF Sensitive File Access TracingPolicy successfully validated!")


if __name__ == "__main__":
    verify()
