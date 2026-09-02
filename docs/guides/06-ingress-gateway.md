# Chapter 06: Ingress & Gateway API

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Ingress Controllers, Path Routing, TLS, and Gateway API
-   :material-api: **Primary APIs** &bull; `networking.k8s.io/v1` &bull; `Ingress`, `IngressClass`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=6){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`ingress01`**: Ingress Host & Path Routing →](../playground/index.html?exercise=ingress01)
    - [**`ingress02`**: Ingress TLS Termination →](../playground/index.html?exercise=ingress02)
    - [**`ingress03`**: Ingress Annotations & Rewrites →](../playground/index.html?exercise=ingress03)
    - [**`ingress04`**: Gateway API Fundamentals →](../playground/index.html?exercise=ingress04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Ingress & Gateway API** is reconciled through declarative state loops managed by the control plane:

```mermaid
flowchart TD
    subgraph Internet["Public Traffic & Edge Clients"]
        USER["Browser / HTTPS Client"]
        DNS["Public DNS (*.example.com)"]
        USER -->|1. DNS Lookup| DNS
    end

    subgraph EdgeLoadBalancer["L4 Cloud Load Balancer / VIP"]
        LB["Cloud Load Balancer (NLB / ALB)<br/><i>Public IP: 203.0.113.50</i>"]
        USER -->|2. TLS SNI Traffic| LB
    end

    subgraph IngressLayer["Ingress Controller (Envoy / NGINX)"]
        ING_POD["Ingress Controller Pods"]
        ING_RES["Ingress Resource Rules<br/><code>Host: api.example.com</code><br/><code>Path: /v1 -> svc-api</code>"]
        ING_RES -->|Configures Routing Table| ING_POD
        LB -->|Routes to NodePort/HostPort| ING_POD
    end

    subgraph ClusterServices["Internal Cluster Microservices"]
        SVC1["Service: svc-api<br/><code>Port 80</code>"]
        SVC2["Service: svc-web<br/><code>Port 80</code>"]
        EP1["Backend Pods: <code>api-fleet</code>"]
        EP2["Backend Pods: <code>web-fleet</code>"]

        ING_POD -->|Reverse Proxy /v1/*| SVC1
        ING_POD -->|Reverse Proxy /*| SVC2
        SVC1 --> EP1
        SVC2 --> EP2
    end
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: production-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-example-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1-service
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2-service
            port:
              number: 80
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.ingressClassName` | `String` | Selects the Ingress controller implementation responsible for parsing this resource. |
| `spec.rules[*].http.paths[*].pathType` | `Enum` | `Prefix` (matches URI prefix), `Exact` (exact URI match), `ImplementationSpecific`. |
| `spec.tls[*].secretName` | `String` | TLS Certificate secret containing `tls.crt` and `tls.key` keys. |

---

## 3. Real-World Architectural Patterns

### Host-Based Virtual Hosting Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-tenant-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: app1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
  - host: app2.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
```

### Canary Traffic Splitting via Ingress Annotations

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "20"
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-canary-service
            port:
              number: 80
```


---

## 4. Production Hardening & Operational Governance

- Enforce TLS 1.3 and automatic HTTP-to-HTTPS redirects across all public routes.
- Integrate `cert-manager` for automated Let's Encrypt TLS certificate lifecycle and renewal.
- Implement rate-limiting and request size restrictions via Ingress controller annotations.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Ingress `404 Not Found`"
    **Root Cause:** Path prefix or hostname does not match Ingress rule definitions.

    **Diagnostic Triage Sequence:**
    1. Verify Ingress rules: `kubectl describe ingress <name>`
    2. Verify Ingress Controller logs: `kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx`

??? failure "Ingress `502 Bad Gateway`"
    **Root Cause:** Target backend Service or Pod is offline or failing health probes.

    **Diagnostic Triage Sequence:**
    1. Verify backend Service endpoints: `kubectl get endpoints <service-name>`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`ingress01`** | Ingress Host & Path Routing | [`../playground/index.html?exercise=ingress01`](../playground/index.html?exercise=ingress01) | [**⚡ Solve `ingress01` in Playground →**](../playground/index.html?exercise=ingress01){ .md-button .md-button--primary } |
| **`ingress02`** | Ingress TLS Termination | [`../playground/index.html?exercise=ingress02`](../playground/index.html?exercise=ingress02) | [**⚡ Solve `ingress02` in Playground →**](../playground/index.html?exercise=ingress02){ .md-button .md-button--primary } |
| **`ingress03`** | Ingress Annotations & Rewrites | [`../playground/index.html?exercise=ingress03`](../playground/index.html?exercise=ingress03) | [**⚡ Solve `ingress03` in Playground →**](../playground/index.html?exercise=ingress03){ .md-button .md-button--primary } |
| **`ingress04`** | Gateway API Fundamentals | [`../playground/index.html?exercise=ingress04`](../playground/index.html?exercise=ingress04) | [**⚡ Solve `ingress04` in Playground →**](../playground/index.html?exercise=ingress04){ .md-button .md-button--primary } |
