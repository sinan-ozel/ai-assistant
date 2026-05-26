# Kubernetes & Helm

agent-stem is designed to run on Kubernetes. Because all agent configuration lives in `cortex/`,
you can run multiple agents in parallel — each with its own Deployment and mounted ConfigMap or PVC.

## Prerequisites

- A running Kubernetes cluster (k3s, k8s, EKS, GKE, AKS, etc.)
- `kubectl` and `helm` installed
- Docker Hub access or a private registry

## Deployment pattern

Each agent is an independent Deployment:

```
┌──────────────────────────────────────────────────────────────────┐
│  Namespace: my-agent                                             │
│                                                                  │
│  Deployment: agent-stem    ← image: sinanozel/ai-assistant:0.1.0 │
│    Volume: cortex-config   ← Volume                              │
│                                                                  │
│  StatefulSet: redis                                              │
│  StatefulSet: qdrant                                             │
└──────────────────────────────────────────────────────────────────┘
```

## Minimal manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-stem
  namespace: my-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: agent-stem
  template:
    metadata:
      labels:
        app: agent-stem
    spec:
      containers:
        - name: agent
          image: sinanozel/ai-assistant:0.1.0
          ports:
            - containerPort: 8000
          env:
            - name: MISTRAL_API_KEY
              valueFrom:
                secretKeyRef:
                  name: llm-secrets
                  key: mistral-api-key
          volumeMounts:
            - name: cortex
              mountPath: /app/cortex
      volumes:
        - name: cortex
          configMap:
            name: agent-cortex
---
apiVersion: v1
kind: Service
metadata:
  name: agent-stem
  namespace: my-agent
spec:
  selector:
    app: agent-stem
  ports:
    - port: 80
      targetPort: 8000
```

## Cortex as a ConfigMap

For small configurations (no binary files), mount the cortex as a ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-cortex
  namespace: my-agent
data:
  providers/default.yaml: |
    api_base: https://api.mistral.ai
    model: mistral/mistral-large-2512
    api_key: ${MISTRAL_API_KEY}
  chat/prompt.py: |
    """You are a helpful assistant."""
    print(input_text)
```

## Cortex with documents (PVC)

For agents with a `library/` of PDFs, use a PersistentVolumeClaim:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cortex-pvc
  namespace: my-agent
spec:
  accessModes:
    - ReadWriteMany   # required for multi-replica deployments
  resources:
    requests:
      storage: 10Gi
```

Then reference it in the Deployment volume:

```yaml
volumes:
  - name: cortex
    persistentVolumeClaim:
      claimName: cortex-pvc
```

Upload your documents to the PVC before or after deployment. The chunking pipeline will
process new files automatically on its next poll cycle.

## Running multiple agents

Because each agent's configuration is just a mounted volume, you can run several agents
in the same cluster simultaneously — each with a different `cortex/`:

```
namespace: search-agent     ← cortex with library/ and search-focused prompt
namespace: coding-agent     ← cortex with coding provider and coding prompt
namespace: extraction-agent ← cortex with workflow YAMLs for data extraction
```

Each namespace gets its own Redis, Qdrant, and agent-stem Deployment.

## Resource recommendations

| Service | CPU request | Memory request | Notes |
|---|---|---|---|
| agent-stem | 500m | 512Mi | Scale replicas for throughput (includes in-process embedding) |
| redis | 100m | 128Mi | Conversation memory |
| qdrant | 250m | 512Mi | Vector store |

For GPU-accelerated local models (llama.cpp, Ollama with CUDA), add a node selector
and resource limit for `nvidia.com/gpu: 1`.

## Context window and hardware constraints

On memory-constrained nodes, set `CONVERSATION_WINDOW_LIMIT` to keep sequence lengths
within hardware limits:

```yaml
env:
  - name: CONVERSATION_WINDOW_LIMIT
    value: "4096"
```

This overrides the model's reported context window without modifying the inference server.
