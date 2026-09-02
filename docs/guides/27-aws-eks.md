# Chapter 27: AWS EKS & Cloud Architecture

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; IRSA, EKS Pod Identity, AWS Load Balancer Controller, VPC CNI, and Karpenter
-   :material-api: **Primary APIs** &bull; `vpcresources.k8s.aws/v1alpha1` &bull; `karpenter.sh/v1` &bull; `alb.ingress.kubernetes.io` &bull; `eks.amazonaws.com`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=27){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`eks01`**: EKS Pod Identity & IRSA ServiceAccounts →](../playground/index.html?exercise=eks01)
    - [**`eks02`**: AWS Load Balancer Controller & ALB Ingress →](../playground/index.html?exercise=eks02)
    - [**`eks03`**: AWS VPC CNI Security Groups for Pods →](../playground/index.html?exercise=eks03)
    - [**`eks04`**: Karpenter NodePool & EC2NodeClass →](../playground/index.html?exercise=eks04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **AWS EKS & Cloud Architecture** is reconciled through declarative state loops managed by the control plane:

```mermaid
flowchart TD
    subgraph IAM_ControlPlane["AWS IAM & STS Control Plane"]
        OIDC["EKS OIDC Provider"]
        IAM_ROLE["AWS IAM Role<br/><code>arn:aws:iam::123:role/s3-reader</code>"]
        STS["AWS Security Token Service (STS)"]
        OIDC <-->|Federated Trust| IAM_ROLE
        IAM_ROLE --> STS
    end

    subgraph EKS_Cluster["Amazon EKS Cluster"]
        K8S_SA["Kubernetes ServiceAccount<br/><code>eks.amazonaws.com/role-arn</code>"]
        WEBHOOK["EKS Pod Mutating Webhook"]
        POD["Application Pod (Worker)"]
        K8S_SA --> POD
        WEBHOOK -->|Injects AWS_WEB_IDENTITY_TOKEN_FILE| POD
    end

    subgraph AWS_VPC_Networking["AWS VPC & Compute Subnets"]
        ALB["AWS Application Load Balancer (ALB)"]
        LBC["AWS Load Balancer Controller"]
        KARPENTER["Karpenter Autoscaler"]
        EC2["EC2 Instances (AL2023 / Spot Fleet)"]
        LBC -->|Provisions Target Groups (IP Mode)| ALB
        ALB -->|Direct Pod Routing| POD
        KARPENTER -->|Right-sized Nodes via Fleet API| EC2
    end

    POD <-->|Assumes Role via Token| STS
    POD <-->|Authorized API Calls| S3[("Amazon S3 / DynamoDB")]
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-reader-sa
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/s3-reader-role
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-ingress
  namespace: default
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `eks.amazonaws.com/role-arn` | `Annotation` | Binds a Kubernetes ServiceAccount to an AWS IAM Role via IAM Roles for Service Accounts (IRSA). |
| `alb.ingress.kubernetes.io/target-type` | `Annotation` | Specifies `ip` for direct Pod IP target routing bypassing NodePort, or `instance` for EC2 node ports. |
| `SecurityGroupPolicy` | `CRD (`vpcresources.k8s.aws`)` | Assigns AWS EC2 security groups directly to pods matching `podSelector` via branch ENIs. |
| `NodePool` & `EC2NodeClass` | `CRD (`karpenter.sh/v1`)` | Configures declarative node provisioning, instance type filtering, spot/on-demand ratios, and AMI families. |

---

## 3. Real-World Architectural Patterns

### AWS VPC CNI SecurityGroupPolicy per Pod

```yaml
apiVersion: vpcresources.k8s.aws/v1alpha1
kind: SecurityGroupPolicy
metadata:
  name: payment-sg-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: payment-gateway
  securityGroups:
    groupIds:
      - sg-0123456789abcdef0
      - sg-0987654321fedcba0
```

### Karpenter v1 NodePool with EC2NodeClass

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default-pool
spec:
  template:
    spec:
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default-nodeclass
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: ["c6i", "c7i", "m6i"]
  limits:
    cpu: "100"
    memory: 400Gi
```


---

## 4. Production Hardening & Operational Governance

- Use EKS Pod Identity or IRSA instead of static IAM credentials or broad EC2 instance profile roles.
- Deploy AWS Load Balancer Controller with target-type `ip` to minimize kube-proxy hop latency.
- Utilize Karpenter for rapid node provisioning and consolidate underutilized nodes automatically.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`WebIdentityErr: failed to retrieve credentials`"
    **Root Cause:** OIDC trust relationship on AWS IAM role is misconfigured or missing audience/subject claims.

    **Diagnostic Triage Sequence:**
    1. Verify OIDC issuer URL: `aws eks describe-cluster --name <cluster> --query cluster.identity.oidc.issuer`
    2. Check IAM Trust Policy `StringEquals` matches `system:serviceaccount:<namespace>:<serviceaccount>`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`eks01`** | EKS Pod Identity & IRSA ServiceAccounts | [`../playground/index.html?exercise=eks01`](../playground/index.html?exercise=eks01) | [**⚡ Solve `eks01` in Playground →**](../playground/index.html?exercise=eks01){ .md-button .md-button--primary } |
| **`eks02`** | AWS Load Balancer Controller & ALB Ingress | [`../playground/index.html?exercise=eks02`](../playground/index.html?exercise=eks02) | [**⚡ Solve `eks02` in Playground →**](../playground/index.html?exercise=eks02){ .md-button .md-button--primary } |
| **`eks03`** | AWS VPC CNI Security Groups for Pods | [`../playground/index.html?exercise=eks03`](../playground/index.html?exercise=eks03) | [**⚡ Solve `eks03` in Playground →**](../playground/index.html?exercise=eks03){ .md-button .md-button--primary } |
| **`eks04`** | Karpenter NodePool & EC2NodeClass | [`../playground/index.html?exercise=eks04`](../playground/index.html?exercise=eks04) | [**⚡ Solve `eks04` in Playground →**](../playground/index.html?exercise=eks04){ .md-button .md-button--primary } |
