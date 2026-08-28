"""
Validators for Chapter 23: Kernel-Level Security & Observability with eBPF Tetragon
"""

from typing import Any

from kubelings.validators import register_validator


def build_tracing_policy() -> dict:
    return {
        "apiVersion": "cilium.io/v1alpha1",
        "kind": "TracingPolicy",
        "metadata": {"name": "audit-process-execution"},
        "spec": {
            "kprobes": [
                {
                    "call": "sys_execve",
                    "syscall": True,
                    "args": [{"index": 0, "type": "string"}],
                    "selectors": [
                        {
                            "matchNamespaces": [
                                {"operator": "In", "values": ["production", "payments"]}
                            ],
                            "matchArgs": [
                                {"index": 0, "operator": "Prefix", "values": ["/bin/", "/usr/bin/"]}
                            ],
                        }
                    ],
                }
            ]
        },
    }


@register_validator("tetragon01")
def validate_tetragon01(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
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


def build_file_monitor_policy() -> dict:
    return {
        "apiVersion": "cilium.io/v1alpha1",
        "kind": "TracingPolicy",
        "metadata": {"name": "monitor-sensitive-file-access"},
        "spec": {
            "kprobes": [
                {
                    "call": "sys_openat",
                    "syscall": True,
                    "args": [{"index": 0, "type": "int"}, {"index": 1, "type": "string"}],
                    "selectors": [
                        {
                            "matchArgs": [
                                {
                                    "index": 1,
                                    "operator": "Prefix",
                                    "values": ["/etc/shadow", "/var/run/secrets/kubernetes.io"],
                                }
                            ]
                        }
                    ],
                }
            ]
        },
    }


@register_validator("tetragon02")
def validate_tetragon02(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
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


def build_enforcement_policy() -> dict:
    return {
        "apiVersion": "cilium.io/v1alpha1",
        "kind": "TracingPolicy",
        "metadata": {"name": "block-privilege-escalation"},
        "spec": {
            "kprobes": [
                {
                    "call": "sys_execve",
                    "syscall": True,
                    "args": [{"index": 0, "type": "string"}],
                    "selectors": [
                        {
                            "matchArgs": [
                                {
                                    "index": 0,
                                    "operator": "Exact",
                                    "values": ["/usr/bin/sudo", "/usr/bin/su", "/usr/bin/nsenter"],
                                }
                            ],
                            "matchActions": [{"action": "Sigkill"}],
                        }
                    ],
                }
            ]
        },
    }


@register_validator("tetragon03")
def validate_tetragon03(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
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


def build_socket_tracing_policy() -> dict:
    return {
        "apiVersion": "cilium.io/v1alpha1",
        "kind": "TracingPolicy",
        "metadata": {"name": "trace-outbound-tcp-connections"},
        "spec": {
            "kprobes": [
                {
                    "call": "tcp_connect",
                    "syscall": False,
                    "args": [{"index": 0, "type": "sock"}],
                    "selectors": [
                        {
                            "matchNamespaces": [
                                {"operator": "In", "values": ["backend", "database"]}
                            ],
                            "matchActions": [{"action": "Post"}],
                        }
                    ],
                }
            ]
        },
    }


@register_validator("tetragon04")
def validate_tetragon04(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
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
