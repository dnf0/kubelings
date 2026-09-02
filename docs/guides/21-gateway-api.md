# Chapter 21: Next-Gen Traffic Routing with Kubernetes Gateway API

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; GatewayClass, Gateway Listeners, HTTPRoute, Canary Traffic Splitting, and ReferenceGrant
-   :material-api: **Primary APIs** &bull; `gateway.networking.k8s.io/v1` &bull; `GatewayClass`, `Gateway`, `HTTPRoute`, `ReferenceGrant`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=21){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`gateway01`**: GatewayClass and Gateway Declaration →](../playground/index.html?exercise=gateway01)
    - [**`gateway02`**: HTTPRoute Path & Header-Based Routing →](../playground/index.html?exercise=gateway02)
    - [**`gateway03`**: Canary Traffic Splitting & URL Rewriting →](../playground/index.html?exercise=gateway03)
    - [**`gateway04`**: Cross-Namespace Security with ReferenceGrant →](../playground/index.html?exercise=gateway04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Next-Gen Traffic Routing with Kubernetes Gateway API** is reconciled through declarative state loops managed by the control plane:

```mermaid
flowchart TD
    subgraph InfrastructureLayer["Infrastructure Role (Cloud / Platform Admin)"]
        GC["GatewayClass: <code>envoy-gateway-class</code><br/><i>Controller: envoyproxy.io/gateway-controller</i>"]
    end

    subgraph ClusterOpsLayer["Cluster Operator Role (Site Ops)"]
        GW["Gateway: <code>prod-gateway</code><br/><i>Listeners: 80 (HTTP), 443 (HTTPS SNI)</i><br/><i>Addresses: 198.51.100.20</i>"]
        GC -->|Instantiates| GW
    end

    subgraph AppDevLayer["Application Developer Role (Team Services)"]
        HTTP_ROUTE["HTTPRoute: <code>store-routes</code><br/><i>Host: store.example.com</i><br/><i>Matches: /cart -> cart-svc, /items -> item-svc</i>"]
        GW -->|Attaches via AllowedRoutes| HTTP_ROUTE
    end

    subgraph BackendWorkloads["Target Service Endpoints"]
        CART_SVC["Service: cart-svc (Weight: 90)"]
        CANARY_SVC["Service: cart-canary-svc (Weight: 10)"]

        HTTP_ROUTE -->|Traffic Splitting| CART_SVC
        HTTP_ROUTE -->|Traffic Splitting| CANARY_SVC
    end
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: external-gateway
  namespace: infra
spec:
  gatewayClassName: envoy-gateway
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    tls:
      mode: Terminate
      certificateRefs:
      - name: tls-cert-example
    allowedRoutes:
      namespaces:
        from: All
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-traffic-split
  namespace: apps
spec:
  parentRefs:
  - name: external-gateway
    namespace: infra
  hostnames:
  - "api.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /v2
    backendRefs:
    - name: api-v2-service
      port: 8080
      weight: 90
    - name: api-v2-canary
      port: 8080
      weight: 10
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `GatewayClass` | `Infrastructure` | Defines the controller implementation (e.g. Envoy Gateway, Cilium, Istio). Managed by Cluster Admins. |
| `Gateway` | `Entrypoint` | Defines network listeners, TLS termination, and allowed route namespaces. |
| `HTTPRoute.spec.rules[*].backendRefs` | `Array` | Defines weighted traffic routing, request header modifications, and url rewriting. |

---

## 3. Real-World Architectural Patterns

### Cross-Namespace ReferenceGrant for TLS Security

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-gateway-tls
  namespace: secrets-vault
spec:
  from:
  - group: gateway.networking.k8s.io
    kind: Gateway
    namespace: infra
  to:
  - group: ""
    kind: Secret
    name: wildcard-tls
```

### Header-Based Canary Route

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: beta-testers-route
  namespace: apps
spec:
  parentRefs:
  - name: external-gateway
    namespace: infra
  rules:
  - matches:
    - headers:
      - name: X-Beta-Tester
        value: "true"
    backendRefs:
    - name: api-beta-svc
      port: 8080
```


---

## 4. Production Hardening & Operational Governance

- Use `allowedRoutes.namespaces` to restrict which namespaces can attach routes to shared Gateway listeners.
- Enforce `ReferenceGrant` when routes or gateways bind to resources in external namespaces.
- Standardize on Gateway API as the next-generation successor to Kubernetes Ingress.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "HTTPRoute `Not Admitted` / `ResolvedRefs=False`"
    **Root Cause:** Parent Gateway not found or ReferenceGrant missing.

    **Diagnostic Triage Sequence:**
    1. Check HTTPRoute status: `kubectl describe httproute <name> -n <namespace>`
    2. Verify Gateway listener conditions: `kubectl describe gateway <name> -n <namespace>`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`gateway01`** | GatewayClass and Gateway Declaration | [`../playground/index.html?exercise=gateway01`](../playground/index.html?exercise=gateway01) | [**⚡ Solve `gateway01` in Playground →**](../playground/index.html?exercise=gateway01){ .md-button .md-button--primary } |
| **`gateway02`** | HTTPRoute Path & Header-Based Routing | [`../playground/index.html?exercise=gateway02`](../playground/index.html?exercise=gateway02) | [**⚡ Solve `gateway02` in Playground →**](../playground/index.html?exercise=gateway02){ .md-button .md-button--primary } |
| **`gateway03`** | Canary Traffic Splitting & URL Rewriting | [`../playground/index.html?exercise=gateway03`](../playground/index.html?exercise=gateway03) | [**⚡ Solve `gateway03` in Playground →**](../playground/index.html?exercise=gateway03){ .md-button .md-button--primary } |
| **`gateway04`** | Cross-Namespace Security with ReferenceGrant | [`../playground/index.html?exercise=gateway04`](../playground/index.html?exercise=gateway04) | [**⚡ Solve `gateway04` in Playground →**](../playground/index.html?exercise=gateway04){ .md-button .md-button--primary } |
