import pytest

from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner
from kubelings.validators import load_all_validators

load_all_validators()


@pytest.fixture(scope="module")
def runner() -> ExerciseRunner:
    return ExerciseRunner()


# ==========================================
# Chapter 27: AWS EKS & Cloud Architecture
# ==========================================


def test_eks01_irsa_serviceaccount(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="eks01",
        title="EKS Pod Identity & IRSA ServiceAccounts",
        path="solutions/27_aws_eks/eks01.yaml",
        chapter_name="27_aws_eks",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"eks01 solution failed: {result.error}"

    starter_ex = Exercise(
        name="eks01",
        title="EKS Pod Identity & IRSA ServiceAccounts",
        path="exercises/27_aws_eks/eks01.yaml",
        chapter_name="27_aws_eks",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_eks02_alb_ingress(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="eks02",
        title="AWS Load Balancer Controller & ALB Ingress",
        path="solutions/27_aws_eks/eks02.yaml",
        chapter_name="27_aws_eks",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"eks02 solution failed: {result.error}"

    starter_ex = Exercise(
        name="eks02",
        title="AWS Load Balancer Controller & ALB Ingress",
        path="exercises/27_aws_eks/eks02.yaml",
        chapter_name="27_aws_eks",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_eks03_security_groups_per_pod(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="eks03",
        title="AWS VPC CNI Security Groups for Pods",
        path="solutions/27_aws_eks/eks03.yaml",
        chapter_name="27_aws_eks",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"eks03 solution failed: {result.error}"

    starter_ex = Exercise(
        name="eks03",
        title="AWS VPC CNI Security Groups for Pods",
        path="exercises/27_aws_eks/eks03.yaml",
        chapter_name="27_aws_eks",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_eks04_karpenter_nodepool(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="eks04",
        title="Karpenter NodePool & EC2NodeClass",
        path="solutions/27_aws_eks/eks04.yaml",
        chapter_name="27_aws_eks",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"eks04 solution failed: {result.error}"

    starter_ex = Exercise(
        name="eks04",
        title="Karpenter NodePool & EC2NodeClass",
        path="exercises/27_aws_eks/eks04.yaml",
        chapter_name="27_aws_eks",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


# ==========================================
# Chapter 28: Google Cloud GKE & Ecosystem
# ==========================================


def test_gke01_workload_identity(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="gke01",
        title="GKE Workload Identity Federation",
        path="solutions/28_gcp_gke/gke01.yaml",
        chapter_name="28_gcp_gke",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"gke01 solution failed: {result.error}"

    starter_ex = Exercise(
        name="gke01",
        title="GKE Workload Identity Federation",
        path="exercises/28_gcp_gke/gke01.yaml",
        chapter_name="28_gcp_gke",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_gke02_autopilot_sizing(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="gke02",
        title="GKE Autopilot Workload Sizing & Compute Classes",
        path="solutions/28_gcp_gke/gke02.yaml",
        chapter_name="28_gcp_gke",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"gke02 solution failed: {result.error}"

    starter_ex = Exercise(
        name="gke02",
        title="GKE Autopilot Workload Sizing & Compute Classes",
        path="exercises/28_gcp_gke/gke02.yaml",
        chapter_name="28_gcp_gke",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_gke03_gateway_cloud_armor(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="gke03",
        title="GKE Gateway API & Cloud Armor Policies",
        path="solutions/28_gcp_gke/gke03.yaml",
        chapter_name="28_gcp_gke",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"gke03 solution failed: {result.error}"

    starter_ex = Exercise(
        name="gke03",
        title="GKE Gateway API & Cloud Armor Policies",
        path="exercises/28_gcp_gke/gke03.yaml",
        chapter_name="28_gcp_gke",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_gke04_config_connector(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="gke04",
        title="Google Config Connector Cloud Resources",
        path="solutions/28_gcp_gke/gke04.yaml",
        chapter_name="28_gcp_gke",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"gke04 solution failed: {result.error}"

    starter_ex = Exercise(
        name="gke04",
        title="Google Config Connector Cloud Resources",
        path="exercises/28_gcp_gke/gke04.yaml",
        chapter_name="28_gcp_gke",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


# =========================================================
# Chapter 29: Enterprise Multi-Account Governance & Secrets
# =========================================================


def test_eso01_external_secrets(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="eso01",
        title="External Secrets Operator SecretStore & ExternalSecret",
        path="solutions/29_enterprise_governance/eso01.yaml",
        chapter_name="29_enterprise_governance",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"eso01 solution failed: {result.error}"

    starter_ex = Exercise(
        name="eso01",
        title="External Secrets Operator SecretStore & ExternalSecret",
        path="exercises/29_enterprise_governance/eso01.yaml",
        chapter_name="29_enterprise_governance",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_vault01_agent_sidecar(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="vault01",
        title="HashiCorp Vault Agent Sidecar Injector",
        path="solutions/29_enterprise_governance/vault01.yaml",
        chapter_name="29_enterprise_governance",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"vault01 solution failed: {result.error}"

    starter_ex = Exercise(
        name="vault01",
        title="HashiCorp Vault Agent Sidecar Injector",
        path="exercises/29_enterprise_governance/vault01.yaml",
        chapter_name="29_enterprise_governance",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_gov01_argocd_applicationset(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="gov01",
        title="ArgoCD ApplicationSet Multi-Cluster Matrix Generator",
        path="solutions/29_enterprise_governance/gov01.yaml",
        chapter_name="29_enterprise_governance",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"gov01 solution failed: {result.error}"

    starter_ex = Exercise(
        name="gov01",
        title="ArgoCD ApplicationSet Multi-Cluster Matrix Generator",
        path="exercises/29_enterprise_governance/gov01.yaml",
        chapter_name="29_enterprise_governance",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed


def test_gov02_multitenant_quotas(runner: ExerciseRunner):
    sol_ex = Exercise(
        name="gov02",
        title="Multi-Tenant Namespace Quotas & Security Policies",
        path="solutions/29_enterprise_governance/gov02.yaml",
        chapter_name="29_enterprise_governance",
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, f"gov02 solution failed: {result.error}"

    starter_ex = Exercise(
        name="gov02",
        title="Multi-Tenant Namespace Quotas & Security Policies",
        path="exercises/29_enterprise_governance/gov02.yaml",
        chapter_name="29_enterprise_governance",
    )
    res_starter = runner.run_exercise(starter_ex)
    assert not res_starter.passed
