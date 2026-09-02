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

In Kubernetes, **AWS EKS & Cloud Architecture** is reconciled through declarative state loops managed by the control plane and node daemons:

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

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **EKS OIDC Provider & IAM Trust Establishment**: An AWS administrator creates an IAM OpenID Connect (OIDC) identity provider for the EKS cluster. An IAM Role is provisioned with a Trust Policy granting `sts:AssumeRoleWithWebIdentity` restricted to a specific Kubernetes ServiceAccount (`system:serviceaccount:default:my-app-sa`).
2. **Projected Token Volume Injection (IRSA / EKS Pod Identity)**:
   - When a Pod referencing `my-app-sa` is submitted, the **EKS Pod Mutating Webhook** intercepts the Pod creation.
   - Injects an ephemeral, cryptographically signed OIDC JWT token into `/var/run/secrets/eks.amazonaws.com/serviceaccount/token`.
   - Injects environment variables: `AWS_ROLE_ARN` and `AWS_WEB_IDENTITY_TOKEN_FILE`.
3. **AWS STS Token Exchange**:
   - The application AWS SDK inside the container reads the projected JWT token file.
   - Calls the AWS Security Token Service (STS) API: `sts:AssumeRoleWithWebIdentity`.
   - AWS STS verifies the token signature against the EKS OIDC discovery endpoint (`https://oidc.eks.amazonaws.com/id/...`).
   - STS issues temporary AWS credentials (AccessKeyId, SecretAccessKey, SessionToken) with 1-hour validity directly to the SDK in memory.
4. **AWS Load Balancer Controller IP-Mode Ingress Routing**:
   - The AWS Load Balancer Controller watches `Ingress` resources annotated with `alb.ingress.kubernetes.io/target-type: ip`.
   - Directly configures AWS Application Load Balancer (ALB) Target Groups with individual Pod private IP addresses allocated by the **AWS VPC CNI**, completely bypassing NodePort hops.
5. **Node Autoscaling via Karpenter**:
   - When pending pods emerge, Karpenter queries EC2 Fleet APIs, calculates the most cost-effective instance types (Graviton, Spot, x86), launches the EC2 instances, and registers them directly with the EKS cluster in under 45 seconds.

### 1.2 Serialization, Protocols & Communication Pathways

- **AWS Signature Version 4 (SigV4) Protocol**: Application SDKs and controllers sign all HTTPS REST requests to AWS APIs using HMAC-SHA256 cryptographic signatures.
- **OIDC Discovery JSON & JWKS Keys**: EKS exposes public JSON Web Key Sets (JWKS) over HTTPS enabling AWS STS to verify cluster-signed JWT tokens.
- **AWS VPC CNI IPAM IPC**: Local IP Address Management daemon (`aws-k8s-cni`) uses Unix domain socket IPC to communicate with kubelet and assign ENI secondary IP addresses directly to Pod network namespaces.

### 1.3 Deep-Dive Component Breakdown

- **IAM Roles for Service Accounts (IRSA)**: Cryptographic identity federation mapping Kubernetes ServiceAccounts directly to AWS IAM Roles without static long-lived credentials.
- **AWS Load Balancer Controller**: Out-of-tree controller managing AWS ALBs, NLBs, and Target Groups in response to Kubernetes Ingress and Service objects.
- **AWS VPC CNI (`amazon-vpc-cni-k8s`)**: High-performance networking plugin allocating native AWS VPC IP addresses and Elastic Network Interfaces (ENIs) directly to Pods.
- **Karpenter**: High-velocity node autoscaler communicating directly with AWS EC2 Fleet and Pricing APIs to provision optimal compute capacity.

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **OIDC Audience Mismatch (`sts:AssumeRoleWithWebIdentity` Fails)**: If the IAM Role Trust Policy specifies `aud: sts.amazonaws.com` but the projected token uses a custom audience, STS rejects the token exchange with `AccessDenied: An error occurred (InvalidIdentityToken)`.
- **VPC Subnet IP Address Exhaustion**: In high-density clusters, the AWS VPC CNI assigns secondary IP addresses from the node's subnet. If the VPC subnet CIDR block runs out of available IPs, new Pods fail to launch with `FailedCreatePodSandBox: no IP addresses available in subnet`.
- **Target Group Registration Lag**: If Pods become ready before the AWS Load Balancer Controller finishes registering their IPs in the ALB Target Group, early traffic receives HTTP 502 Bad Gateway errors. Configure a `readinessGate` (`target-health.alb.ingress.kubernetes.io`) on the Pod to prevent traffic routing until target registration health checks pass.

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
