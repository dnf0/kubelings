# Chapter 09: Network Policies & Traffic Segmentation

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Default Deny, Ingress/Egress Isolation, and IPBlock Rules
-   :material-api: **Primary APIs** &bull; `networking.k8s.io/v1` &bull; `NetworkPolicy`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=9){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Network Policies & Traffic Segmentation** is reconciled through declarative state loops managed by the control plane:

```text
┌─────────────────────────────────────────────────────────────┐
    │                     Frontend Namespace                      │
    │   [ Frontend Pod ] ──(Port 5432 TCP)───┐                    │
    └────────────────────────────────────────┼────────────────────┘
                                             │ Allowed Ingress
                                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                     Database Namespace                      │
    │   ┌─────────────────────────────────────────────────────┐   │
    │   │           NetworkPolicy: Allow-From-Frontend        │   │
    │   │   [ PostgreSQL Pod (Port 5432) ]                    │   │
    │   │   Default Deny All Other Ingress / Egress           │   │
    │   └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

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
| **`netpol01`** | Default Deny Network Policy | [`../playground/index.html?exercise=netpol01`](../playground/index.html?exercise=netpol01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=netpol01){ .md-button .md-button--primary } |
| **`netpol02`** | Ingress Traffic Filtering | [`../playground/index.html?exercise=netpol02`](../playground/index.html?exercise=netpol02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=netpol02){ .md-button .md-button--primary } |
| **`netpol03`** | Egress Traffic & DNS Access | [`../playground/index.html?exercise=netpol03`](../playground/index.html?exercise=netpol03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=netpol03){ .md-button .md-button--primary } |
| **`netpol04`** | Named Ports & IPBlock CIDR Exceptions | [`../playground/index.html?exercise=netpol04`](../playground/index.html?exercise=netpol04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=netpol04){ .md-button .md-button--primary } |
