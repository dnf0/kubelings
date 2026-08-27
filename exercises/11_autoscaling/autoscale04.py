"""
Exercise: exercises/11_autoscaling/autoscale04.py
Topic: Event-Driven Autoscaling (KEDA)

Instructions:
KEDA (Kubernetes Event-driven Autoscaling) allows workloads to scale dynamically
based on external event sources (e.g. RabbitMQ queues, Kafka topics, AWS SQS,
or Prometheus metrics). Crucially, KEDA can scale deployments down to 0 replicas
when there are no events to process, and scale up from 0 when events arrive.

1. Define a KEDA ScaledObject 'orders-queue-scaler' in namespace 'messaging':
   - apiVersion: keda.sh/v1alpha1
   - kind: ScaledObject
   - scaleTargetRef:
     - apiVersion: apps/v1
     - kind: Deployment
     - name: order-consumer
   - minReplicaCount: 0
   - maxReplicaCount: 30
   - pollingInterval: 15
   - cooldownPeriod: 300
   - triggers:
     - type: rabbitmq
       metadata:
         queueName: orders-queue
         queueLength: "20"
         mode: QueueLength
         host: amqp://guest:guest@rabbitmq.messaging.svc.cluster.local:5672
"""

import yaml

from kubelings.validator import validate_manifest

SCALED_OBJECT_MANIFEST = """
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: orders-queue-scaler
  namespace: messaging
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ???
  minReplicaCount: ???
  maxReplicaCount: ???
  pollingInterval: ???
  cooldownPeriod: 300
  triggers:
  - type: ???
    metadata:
      queueName: orders-queue
      queueLength: "20"
      mode: QueueLength
      host: amqp://guest:guest@rabbitmq.messaging.svc.cluster.local:5672
"""


def verify():
    manifest = yaml.safe_load(SCALED_OBJECT_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="ScaledObject",
        expected_api_version="keda.sh/v1alpha1",
    )

    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "orders-queue-scaler"
    assert metadata.get("namespace") == "messaging"

    spec = manifest.get("spec", {})
    scale_target = spec.get("scaleTargetRef", {})
    assert scale_target.get("apiVersion") == "apps/v1"
    assert scale_target.get("kind") == "Deployment"
    assert scale_target.get("name") == "order-consumer"

    assert spec.get("minReplicaCount") == 0, (
        "minReplicaCount must be 0 for scale-to-zero capability"
    )
    assert spec.get("maxReplicaCount") == 30, "maxReplicaCount must be 30"
    assert spec.get("pollingInterval") == 15, "pollingInterval must be 15 seconds"
    assert spec.get("cooldownPeriod") == 300, "cooldownPeriod must be 300 seconds"

    triggers = spec.get("triggers", [])
    assert len(triggers) == 1, "Must define exactly 1 trigger"
    trigger = triggers[0]
    assert trigger.get("type") == "rabbitmq"
    trig_meta = trigger.get("metadata", {})
    assert trig_meta.get("queueName") == "orders-queue"
    assert trig_meta.get("queueLength") == "20"
    assert trig_meta.get("mode") == "QueueLength"
    assert "amqp://" in trig_meta.get("host", "")

    print("✓ autoscale04 passed!")


if __name__ == "__main__":
    verify()
