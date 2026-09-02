# Chapter 09: Network Policies & Traffic Segmentation

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Default Deny, Ingress/Egress Isolation, and IPBlock Rules
-   :material-api: **Primary APIs** &bull; `networking.k8s.io/v1` &bull; `NetworkPolicy`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=9){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`netpol01`**: Default Deny Network Policy →](../playground/index.html?exercise=netpol01)
    - [**`netpol02`**: Ingress Traffic Filtering →](../playground/index.html?exercise=netpol02)
    - [**`netpol03`**: Egress Traffic & DNS Access →](../playground/index.html?exercise=netpol03)
    - [**`netpol04`**: Named Ports & IPBlock CIDR Exceptions →](../playground/index.html?exercise=netpol04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Network Policies & Traffic Segmentation** is reconciled through declarative state loops managed by the control plane and node daemons:

```mermaid
flowchart TD
    subgraph IngressSource["Traffic Sources"]
        SRC_APP["Frontend Pod (app=frontend)"]
        SRC_EXT["External IP (192.168.1.0/24)"]
        SRC_ROGUE["Untrusted Pod (app=untrusted)"]
    end

    subgraph PolicyEngine["CNI Datapath Firewall (eBPF / iptables)"]
        NETPOL["NetworkPolicy: <code>db-netpol</code><br/><i>podSelector: app=database</i><br/><i>policyTypes: [Ingress, Egress]</i>"]
        ALLOW_RULE["Ingress Rules:<br/>- from: [podSelector: app=frontend]<br/>- ports: [5432/TCP]"]
        DENY_ALL["Default-Deny Isolation Barrier"]
        NETPOL --> ALLOW_RULE
        NETPOL --> DENY_ALL
    end

    subgraph ProtectedWorkload["Isolated Database Pod"]
        DB["Target Pod: <code>app=database</code><br/><i>Port 5432 (Postgres)</i>"]
    end

    SRC_APP -->|Allowed (Matches Selector & Port)| DB
    SRC_EXT -->|Blocked (CIDR Not Whitelisted)| DENY_ALL
    SRC_ROGUE -->|Dropped by Kernel Datapath| DENY_ALL
```

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **NetworkPolicy Resource Submission**: An operator applies a `networking.k8s.io/v1 NetworkPolicy` targeting a specific set of Pods via `spec.podSelector: { matchLabels: { app: database } }`.
2. **Default-Deny Isolation Enforcement**: The declaration of `policyTypes: [Ingress, Egress]` immediately transitions all selected Pods into an isolated state. All traffic not explicitly allowed by the policy rules is dropped by the kernel.
3. **CNI Agent Rule Compilation**: The CNI daemon running on each worker node (Cilium, Calico, or kube-router) watches NetworkPolicy resources:
   - **eBPF Mode (Cilium)**: Compiles the policy rules into BPF bytecode, updating in-kernel BPF maps (`cilium_policy`) attached to the Pod's network interfaces.
   - **iptables Mode (Calico)**: Writes targeted Netfilter chains (`cali-pi-*` for ingress, `cali-po-*` for egress) with ipset match sets.
4. **Ingress Rule Evaluation**: Incoming packets destined for the database Pod are inspected:
   - **Allowed Traffic**: Packets originating from source Pods matching `podSelector: { app: frontend }` on TCP port `5432` match the allow rule and are forwarded directly to the container socket.
   - **Blocked / Dropped Traffic**: Packets originating from untrusted Pods or external IP ranges not matching explicit CIDR whitelists (`ipBlock`) fail all allow rules and are immediately dropped at the kernel socket or tc layer without returning TCP RST.

### 1.2 Serialization, Protocols & Communication Pathways

- **eBPF Map Binary Data Structures**: Network policy endpoints and CIDRs are written into in-kernel hash maps (`BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_LPM_TRIE`) for $O(1)$ prefix matching in the kernel.
- **Netlink / ipset Control Plane**: Calico and iptables-based CNIs serialize IP sets and port bitmasks over Linux Netlink sockets into kernel memory tables.
- **Protobuf API Watch**: CNI node daemons stream NetworkPolicy, Pod, and Namespace state from `kube-apiserver` using HTTP/2 Protobuf connections.

### 1.3 Deep-Dive Component Breakdown

- **CNI Node Agent (Cilium Agent / Calico Felix)**: Privileged host daemon that translates high-level Kubernetes label-based network policies into hardware or kernel-level packet filter rules.
- **Linux TC (Traffic Control) & XDP Hooks**: eBPF attachment points at the network driver (XDP) or kernel queuing discipline (TC) processing packets before they enter the TCP/IP stack.
- **Linux Netfilter Conntrack**: Stateful connection tracking table that automatically allows return traffic for established TCP connections without requiring reciprocal egress rules.
- **LPM (Longest Prefix Match) Trie**: In-kernel algorithmic data structure used for high-speed IP CIDR classification (`10.0.0.0/16`).

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **Missing CNI Plugin Enforcement**: Standard default Kubernetes networking (e.g. basic Flannel) does **not** enforce NetworkPolicies. NetworkPolicy objects are accepted by `kube-apiserver` without errors, but packets are routed freely with zero isolation unless an enforcement-capable CNI (Cilium, Calico) is installed.
- **Loopback & Host Network Egress Blocks**: An over-restrictive egress policy (`policyTypes: [Egress]` without DNS rules) will block access to CoreDNS (`10.96.0.10:53`), causing all internal service name resolutions to fail with timeout errors.
- **Cross-Namespace Selector Omission**: In `from.namespaceSelector`, omitting the namespace selector restricts matching strictly to Pods within the **same** namespace. To allow ingress from a frontend pod in another namespace, both `namespaceSelector` and `podSelector` must be defined concurrently.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.podSelector` | `Object` | Selects target Pods governed by this policy. Empty `{}` matches all Pods in namespace. |
| `spec.policyTypes` | `Array` | `Ingress` (inbound traffic control), `Egress` (outbound traffic control). |
| `spec.ingress[*].from` | `Array` | List of allowed sources. Multiple elements in single block are OR-ed; elements in separate blocks are AND-ed. |

---

## 3. Real-World Architectural Patterns

### Default Deny All Ingress Traffic

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: secure-zone
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

### Allow Egress Only to DNS and Internal CIDR

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: worker
  policyTypes:
  - Egress
  egress:
  - ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
  - to:
    - ipBlock:
        cidr: 10.0.0.0/16
        except:
        - 10.0.100.0/24
```


---

## 4. Production Hardening & Operational Governance

- Start with a namespace-wide `default-deny-ingress` and `default-deny-egress` policy and explicitly allowlist required traffic flows.
- Always include egress rules for CoreDNS (`kube-system` UDP/TCP port 53); otherwise, name resolution inside Pods will fail.
- Verify that your CNI plugin (e.g. Cilium, Calico, Antrea) actively enforces NetworkPolicy resources.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Pod Cannot Connect to Remote Service / DNS Timeout"
    **Root Cause:** Egress policy is blocking traffic to CoreDNS or backend CIDR.

    **Diagnostic Triage Sequence:**
    1. Verify CNI policy enforcement status.
    2. Temporarily test DNS with: `kubectl exec -it <pod> -- nslookup kubernetes.default`
    3. Verify ingress/egress port and namespaceSelector definitions.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`netpol01`** | Default Deny Network Policy | [`../playground/index.html?exercise=netpol01`](../playground/index.html?exercise=netpol01) | [**⚡ Solve `netpol01` in Playground →**](../playground/index.html?exercise=netpol01){ .md-button .md-button--primary } |
| **`netpol02`** | Ingress Traffic Filtering | [`../playground/index.html?exercise=netpol02`](../playground/index.html?exercise=netpol02) | [**⚡ Solve `netpol02` in Playground →**](../playground/index.html?exercise=netpol02){ .md-button .md-button--primary } |
| **`netpol03`** | Egress Traffic & DNS Access | [`../playground/index.html?exercise=netpol03`](../playground/index.html?exercise=netpol03) | [**⚡ Solve `netpol03` in Playground →**](../playground/index.html?exercise=netpol03){ .md-button .md-button--primary } |
| **`netpol04`** | Named Ports & IPBlock CIDR Exceptions | [`../playground/index.html?exercise=netpol04`](../playground/index.html?exercise=netpol04) | [**⚡ Solve `netpol04` in Playground →**](../playground/index.html?exercise=netpol04){ .md-button .md-button--primary } |
