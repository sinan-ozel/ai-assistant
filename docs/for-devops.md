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

### Public vs private endpoints

All endpoints whose path starts with `/private` are intended for internal use only — the Streamlit UI, monitoring, and operator tooling. They are not authenticated and must not be reachable from the public internet.

The expected deployment model is an ingress or reverse proxy that forwards only the public paths (`/v1/`, `/health`, `/docs`) and blocks everything under `/private`. For example, with an nginx ingress:

```yaml
# Only forward public paths — drop /private/* at the ingress
nginx.ingress.kubernetes.io/configuration-snippet: |
  location /private/ {
    return 403;
  }
```

Or with a path-based rule in your Ingress resource — route `/v1/` and `/health` to the service, and define no rule for `/private/` so it never reaches the pods from outside the cluster.

The Streamlit UI (port 8501) is also internal-only. Expose it only within the cluster or over a VPN — never directly to the internet.

---

## Process model and container lifecycle

Each container runs two processes managed by supervisord:

| Process | Port | Role | Restart policy |
|---|---|---|---|
| **FastAPI** | 8000 | Production backend | None — container exits when it exits |
| **Streamlit** | 8501 | Dev/test UI | Automatic restart on crash |

### Fail-fast backend

FastAPI is the only process that matters in production. If it encounters a fatal condition at startup — an unreachable MCP tool server, a missing or invalid provider, a misconfigured cortex — it exits immediately. A supervisord event listener detects the exit and shuts down the entire container.

The exit code is propagated correctly:
- **Non-zero exit** (startup error, fatal condition) → container exits with code **1** → Kubernetes reports `Reason: Error`
- **Normal shutdown** (`docker stop`, SIGTERM from Kubernetes) → container exits with code **0** → Kubernetes reports `Reason: Completed`

This means your liveness and readiness probes, restart policies, and alerting all behave as expected without any special configuration.

### Streamlit is not a production component

Streamlit is a personal development and testing UI. Its crash-and-restart behavior is intentional — a failed Streamlit process does not indicate a backend problem and does not affect the container's exit code. In production deployments you should:

- Block port 8501 at the ingress or with a Kubernetes NetworkPolicy
- Not define a liveness probe on port 8501
- Ignore Streamlit restarts in your alerting rules

### Kubernetes probe guidance

Because FastAPI fails fast on startup errors, `initialDelaySeconds` can be kept short. There is no value in a long startup grace period — a broken agent will exit cleanly rather than sitting unhealthy indefinitely.

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

Provider discovery runs in the background after startup, so the `/health` endpoint returns 200 before all providers are confirmed available. If you need to gate traffic until providers are ready, poll `GET /private/v1/providers` and check that `loading` is `false` in the response.

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

## Multi-tenancy

agent-stem is not a full multi-tenant SaaS platform. The design assumption is that it runs behind a trusted proxy or ingress that handles authentication and user identity, then injects that identity into each request. The agent service itself does no authentication.

### How user isolation works

Every conversation is stored in Redis under the key `user_id:conversation_id`. Two callers using the same `conversation_id` string but different `user_id` values get completely separate conversation histories and will never see each other's messages.

When `user_id` is not supplied the service falls back to `"default-user"`, which means all unauthenticated callers share a single namespace — only suitable for single-user or development deployments.

### Injecting user identity from the proxy

The proxy should set the `User-Id` request header on every forwarded request. The agent reads it and uses it as the effective user ID:

```
POST /v1/agent/chat
User-Id: alice@example.com
Content-Type: application/json

{"message": "Hello"}
```

The `user_id` field in the JSON body is also accepted for cases where the client controls its own identity (e.g. during development). If both are present they must match after whitespace trimming; a mismatch returns `400 Bad Request`.

```nginx
# nginx: inject the authenticated user from upstream auth
proxy_set_header User-Id $authenticated_user;
```

```yaml
# Kubernetes ingress-nginx: inject from an auth sub-request result
nginx.ingress.kubernetes.io/auth-url: "https://auth.internal/validate"
nginx.ingress.kubernetes.io/auth-response-headers: "X-Auth-User"
nginx.ingress.kubernetes.io/configuration-snippet: |
  proxy_set_header User-Id $http_x_auth_user;
  location /private/ {
    return 403;
  }
```

### What the proxy must enforce

| Responsibility | Where it belongs |
|---|---|
| Authentication (login, tokens, sessions) | Proxy / ingress |
| Injecting `User-Id` header | Proxy / ingress |
| Blocking `/private/*` from the public internet | Proxy / ingress |
| Conversation isolation between users | agent-stem (automatic once `User-Id` is set) |

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
