# For the DevOps — Running in Production

This page covers deploying agent-stem to a Kubernetes cluster with Helm.

---

## Architecture overview

agent-stem is a stateless, horizontally-scalable service. The agent container itself holds no state:

- **Redis** stores conversation history
- **Qdrant** stores the vector index
- **The model server** (cloud API or self-hosted) is external

You can run as many agent replicas as you need behind a load balancer. All replicas share the same Redis and Qdrant.

```
                     ┌─────────────────────────────┐
                     │  Load Balancer               │
                     └────────────┬────────────────-┘
               ┌──────────────────┼──────────────────┐
        ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
        │  agent pod  │    │  agent pod  │    │  agent pod  │
        └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
               └──────────────────┼──────────────────┘
                     ┌────────────┼────────────┐
                  ┌──┴──┐     ┌───┴───┐   ┌────┴────┐
                  │Redis│     │Qdrant │   │LLM API  │
                  └─────┘     └───────┘   └─────────┘
```

The cortex is mounted into pods via a Kubernetes ConfigMap or PersistentVolume. The container image is on Docker Hub as `sinanozel/agent-stem`.

---

## Helm chart

A Helm chart ships with the repository at `helm/ai-assistant`. Basic install:

```bash
helm upgrade --install my-agent ./helm/ai-assistant \
  --set image.tag=0.1.0 \
  --wait
```

---

## Delivering the cortex to pods

### Option 1: ConfigMap (small cortexes, no binary files)

Create the ConfigMap from your files:

```bash
kubectl create configmap my-agent-cortex \
  --from-file=cortex/providers/default.yaml \
  --from-file=cortex/chat/prompt.py
```

Reference it in `values.yaml`:

```yaml
cortex:
  configMapName: my-agent-cortex
```

ConfigMaps have a 1 MB limit. Use a PVC if your `cortex/library/` contains PDFs.

### Option 2: PersistentVolume (large document libraries)

```yaml
cortex:
  pvcName: my-agent-cortex-pvc
```

The PVC must be pre-populated with your library files before the agent starts. A typical pattern is an init container or a separate indexing job that writes to the PVC.

---

## Secrets management

Never put API keys in `values.yaml` or ConfigMaps. Create a Kubernetes Secret:

```bash
kubectl create secret generic llm-secrets \
  --from-literal=MISTRAL_API_KEY=sk-... \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-...
```

Reference it in `values.yaml`:

```yaml
extraEnvFromSecret: llm-secrets
```

Your `cortex/providers/default.yaml` can then use `${MISTRAL_API_KEY}` as usual — the variable is injected from the Secret at runtime, not stored in the config file.

---

## Scaling replicas

```yaml
# values.yaml
replicaCount: 5
```

Because the agent is stateless, scaling horizontally is safe. All replicas share the same Redis (conversation history) and Qdrant (vector index).

The document indexing pipeline runs inside each pod. If you have many replicas and a large library, stagger the polling intervals or run the pipeline in a dedicated pod and disable it on agent replicas:

```yaml
# values.yaml
env:
  - name: PDF_CHECK_INTERVAL_SECONDS
    value: "300"
  - name: CHUNK_CHECK_INTERVAL_SECONDS
    value: "600"
```

---

## VRAM constraints with self-hosted models

If you are running a local model with limited GPU memory, cap the token budget sent on each request:

```yaml
# values.yaml
env:
  - name: CONVERSATION_WINDOW_LIMIT
    value: "4096"
```

Full conversation history is always stored in Redis. This limit only controls how much history is forwarded to the model per request. The same limit applies at the inference server level — set `-c 4096` in your llama.cpp flags or equivalent.

Known context windows from test environments:
- `gemma3:270m` via Ollama: 32,768 tokens
- `mistral-large` via Mistral API: 128,000 tokens

---

## Health and readiness probes

```bash
curl http://your-agent/health
# → 200 OK
```

Use as both liveness and readiness probe:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 15
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## Checking provider status

```bash
curl http://your-agent/private/v1/providers
```

Returns which providers are loaded, which is the default, and whether each validated successfully. Useful for debugging startup failures in a cluster environment.

---

## Example: full `values.yaml` for production

```yaml
replicaCount: 3

image:
  repository: sinanozel/agent-stem
  tag: "0.1.0"

extraEnvFromSecret: llm-secrets

env:
  - name: CONVERSATION_WINDOW_LIMIT
    value: "8192"
  - name: LOG_LEVEL
    value: "INFO"

cortex:
  configMapName: my-agent-cortex

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
```

---

## Runnable examples with Helm values

Each directory under `examples/` includes a `helm/values.yaml` ready for use:

| Example | Description |
|---|---|
| [hello_world](../examples/hello_world/) | Minimal — just a provider, no customization |
| [bakery_agent](../examples/bakery_agent/) | Chat agent with documents and personality |
| [basic_example](../examples/basic_example/) | Agent with a workflow endpoint |
