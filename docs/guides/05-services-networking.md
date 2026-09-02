# Chapter 05: Services & Networking

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; ClusterIP, Headless, NodePort, LoadBalancer, and CoreDNS
-   :material-api: **Primary APIs** &bull; `v1`, `discovery.k8s.io/v1` &bull; `Service`, `EndpointSlice`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=5){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`net01`**: ClusterIP Services & Port Mapping →](../playground/index.html?exercise=net01)
    - [**`net02`**: Headless Services & Stateful Addressing →](../playground/index.html?exercise=net02)
    - [**`net03`**: NodePort & LoadBalancer Service Types →](../playground/index.html?exercise=net03)
    - [**`net04`**: CoreDNS Internal Service Resolution →](../playground/index.html?exercise=net04)
    - [**`net05`**: ExternalName Services & Manual Endpoints →](../playground/index.html?exercise=net05)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Services & Networking** is reconciled through declarative state loops managed by the control plane and node daemons:

```mermaid
flowchart TD
    subgraph ClientLayer["Client Pods & External Traffic"]
        CLIENT["Client Pod<br/><code>10.244.1.15</code>"]
        DNS["CoreDNS<br/><code>service.namespace.svc.cluster.local</code>"]
        CLIENT -->|1. Resolve DNS| DNS
        DNS -->|2. Returns ClusterIP 10.96.0.10| CLIENT
    end

    subgraph ServiceRouting["Kernel Datapath (kube-proxy)"]
        VIP["Service VIP: <code>10.96.0.10:80</code><br/><i>(iptables PREROUTING / IPVS)</i>"]
        EPS["EndpointSlice Controller<br/><i>Tracks healthy Pod IPs</i>"]
        VIP <-->|Watches| EPS
    end

    subgraph TargetPods["Backend Pod Endpoints (Direct Pod CNI IPs)"]
        POD1["Pod A: <code>10.244.2.40:8080</code><br/><i>(Ready)</i>"]
        POD2["Pod B: <code>10.244.3.82:8080</code><br/><i>(Ready)</i>"]
        POD3["Pod C: <code>10.244.1.99:8080</code><br/><i>(Ready)</i>"]
    end

    CLIENT -->|3. TCP SYN to VIP| VIP
    VIP -->|DNAT Packet Load Balance| POD1
    VIP -->|DNAT Packet Load Balance| POD2
    VIP -->|DNAT Packet Load Balance| POD3
```

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **Service Registration & VIP Allocation**: An operator creates a `v1/Service` with `spec.type: ClusterIP` and selector `app: payment-api`. `kube-apiserver` assigns an immutable Virtual IP (VIP) from the preconfigured CIDR block (e.g., `10.96.0.0/12`).
2. **EndpointSlice Controller Reconciliation**: The `EndpointSlice` controller inside `kube-controller-manager` queries the informer cache for all running Pods whose labels match `app: payment-api` and whose `status.conditions[Ready]` is `True`. It populates `discovery.k8s.io/v1 EndpointSlice` objects containing lists of direct Pod CNI IP addresses and ports.
3. **CoreDNS A-Record Resolution**: When a client Pod executes an HTTP request to `http://payment-api.default.svc.cluster.local`, the local Linux resolver sends a DNS query over UDP 53 to CoreDNS. CoreDNS responds with the Service ClusterIP VIP (`10.96.0.10`).
4. **Kernel Datapath Packet Interception (`kube-proxy`)**: The client container initiates a TCP SYN packet addressed to `10.96.0.10:80`. As the packet traverses the host kernel networking stack:
   - **iptables Mode**: Netfilter traverses the `KUBE-SERVICES` chain to `KUBE-SVC-XXX`, applying random probabilistic matching (`-m statistic --mode random --probability 0.33`) to select an endpoint, executing Destination NAT (DNAT) to rewrite the destination IP to the real Pod IP (`10.244.2.40:8080`).
   - **IPVS Mode**: The kernel IP Virtual Server (IPVS) module performs direct hash-table lookups (`ipset`) in $O(1)$ time complexity, routing the packet to the selected backend.
   - **eBPF Mode (Cilium)**: eBPF programs attached to the cgroup socket egress (`sockops`) rewrite the destination IP and port in the socket data structure before packets are even emitted to the network stack.
5. **Direct CNI Pod Delivery**: The rewritten IP packet traverses the overlay or direct routing CNI network (Calico, Cilium, AWS VPC CNI) directly to the target Pod's `veth` interface, where the application process processes the request and responds.

### 1.2 Serialization, Protocols & Communication Pathways

- **DNS RFC 1035 UDP/TCP Wire Protocol**: CoreDNS processes binary DNS requests over port 53, caching A, AAAA, and SRV record lookups in-memory.
- **Netlink System Calls**: `kube-proxy` in IPVS mode uses Linux Netlink sockets (`AF_NETLINK`) to program kernel IPVS virtual servers and `ipset` collections directly without spawning shell processes.
- **Protobuf API Streaming**: The EndpointSlice controller streams high-scale endpoint updates over Protobuf connections to avoid JSON serialization bottlenecks in clusters with tens of thousands of pods.

### 1.3 Deep-Dive Component Breakdown

- **CoreDNS**: High-performance, plugin-based DNS server running in `kube-system`, dynamically configured via Kubernetes API watches to serve cluster-internal service discovery.
- **kube-proxy**: Node daemon responsible for reflecting Kubernetes Service definitions into Linux kernel Netfilter (`iptables`), IPVS, or user-space routing tables.
- **EndpointSlice**: Scalable replacement for legacy `v1.Endpoints`, splitting large endpoint lists into chunks of up to 100 endpoints to minimize network traffic and API server serialization latency on large deployments.
- **Linux Netfilter & Conntrack**: Kernel connection tracking subsystem that stores active bidirectional TCP/UDP flow state in `/proc/net/nf_conntrack`, enabling accurate reverse SNAT/DNAT on reply packets.

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **Conntrack Table Saturation**: High connection churn without TCP connection reuse can exceed `nf_conntrack_max`, causing the kernel to drop new TCP SYN packets silently with `nf_conntrack: table full, dropping packet`.
- **Stale Endpoints During Rolling Updates**: If a terminating Pod does not immediately unregister from the EndpointSlice before shutting down its HTTP server, incoming in-flight TCP requests receive `TCP RST` (Connection Refused) errors. Implementing a `preStop` hook (`sleep 5`) gives the EndpointSlice controller time to propagate removal across all nodes.
- **CoreDNS 5-Second DNS Lookup Delays**: Linux `glibc` sends IPv4 (A) and IPv6 (AAAA) DNS queries concurrently over UDP. Netfilter conntrack race conditions can cause one query to be dropped, triggering a full 5-second glibc DNS retry timeout (mitigated by configuring `single-request-reopen` in `/etc/resolv.conf` or deploying NodeLocal DNSCache).

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
  labels:
    app: backend
spec:
  type: ClusterIP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
  selector:
    app: backend
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.type` | `Enum` | `ClusterIP` (internal virtual IP), `NodePort` (dedicated port on all nodes), `LoadBalancer` (cloud provider VIP), `ExternalName` (CNAME redirect). |
| `spec.clusterIP: None` | `String` | Creates a Headless Service; DNS queries return raw Pod IPs directly instead of a virtual VIP. |
| `spec.ports[*].targetPort` | `Integer / String` | The destination port exposed by container processes in matching Pods. |

---

## 3. Real-World Architectural Patterns

### Headless Service for Stateful Workloads

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kafka-headless
spec:
  clusterIP: None
  selector:
    app: kafka
  ports:
  - name: tcp-kafka
    port: 9092
    targetPort: 9092
```

### ExternalName Service for Cloud SaaS Integration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ExternalName
  externalName: db.production.rds.amazonaws.com
```


---

## 4. Production Hardening & Operational Governance

- Use `ClusterIP` as default; avoid exposing services as `NodePort` directly to public networks.
- Configure readiness probes on Pods to guarantee traffic is routed only to warm, healthy endpoints.
- Audit `EndpointSlice` scaling for large workloads (>1,000 pods) to prevent control plane memory pressure.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Service Has No Endpoints (`503` / Connection Refused)"
    **Root Cause:** Service selector does not match any Pod labels, or Pod readiness probes are failing.

    **Diagnostic Triage Sequence:**
    1. Check matching endpoints: `kubectl get endpoints <service-name>`
    2. Verify Pod labels: `kubectl get pods --show-labels`
    3. Verify container port binding: `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].ports}'`

??? failure "CoreDNS Name Resolution Failure"
    **Root Cause:** DNS lookup fails for `service.namespace.svc.cluster.local`.

    **Diagnostic Triage Sequence:**
    1. Test from inside cluster: `kubectl run curl --rm -it --image=curlimages/curl -- nslookup <service-name>`
    2. Check CoreDNS pods: `kubectl get pods -n kube-system -l k8s-app=kube-dns`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`net01`** | ClusterIP Services & Port Mapping | [`../playground/index.html?exercise=net01`](../playground/index.html?exercise=net01) | [**⚡ Solve `net01` in Playground →**](../playground/index.html?exercise=net01){ .md-button .md-button--primary } |
| **`net02`** | Headless Services & Stateful Addressing | [`../playground/index.html?exercise=net02`](../playground/index.html?exercise=net02) | [**⚡ Solve `net02` in Playground →**](../playground/index.html?exercise=net02){ .md-button .md-button--primary } |
| **`net03`** | NodePort & LoadBalancer Service Types | [`../playground/index.html?exercise=net03`](../playground/index.html?exercise=net03) | [**⚡ Solve `net03` in Playground →**](../playground/index.html?exercise=net03){ .md-button .md-button--primary } |
| **`net04`** | CoreDNS Internal Service Resolution | [`../playground/index.html?exercise=net04`](../playground/index.html?exercise=net04) | [**⚡ Solve `net04` in Playground →**](../playground/index.html?exercise=net04){ .md-button .md-button--primary } |
| **`net05`** | ExternalName Services & Manual Endpoints | [`../playground/index.html?exercise=net05`](../playground/index.html?exercise=net05) | [**⚡ Solve `net05` in Playground →**](../playground/index.html?exercise=net05){ .md-button .md-button--primary } |
