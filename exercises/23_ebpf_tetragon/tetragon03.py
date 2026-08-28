"""
Exercise: tetragon03.py
Topic: eBPF Security - Real-Time Kernel Enforcement and Sigkill Actions

Context & Why:
Passive security auditing is insufficient against automated zero-day exploits and rapid lateral
movement; by the time an alert reaches an operator, data may already be compromised.

Tetragon bridges observability and active defense through synchronous in-kernel enforcement:
- Evaluates policy rules directly inside the kernel execution path before the system call returns.
- If a prohibited binary execution (such as `sudo`, `su`, or container breakout tools like `nsenter`)
  matches the filter (`matchArgs: [{operator: 'Exact', values: [...]}]`), Tetragon immediately executes
  a kernel-level enforcement action (`matchActions: [{action: 'Sigkill'}]`).
- Sending `SIGKILL` directly from the eBPF hook terminates the offending process instantly before it can
  execute a single instruction or spawn child processes, eliminating user-space race conditions.

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
    # TODO: Define and return the Tetragon TracingPolicy manifest configured with in-kernel Sigkill enforcement for unauthorized binaries.
    # WHY: Synchronous in-kernel enforcement with Sigkill terminates malicious processes instantly at the syscall boundary,
    #      preventing unauthorized privilege escalation before any malicious instructions or exploit payloads can execute.
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
