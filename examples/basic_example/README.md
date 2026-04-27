# Basic Example

A minimal ai-assistant deployment: a helpful chat assistant with no documents and no workflows.
The provider in `cortex/providers/default.yaml` is pre-configured for llama.cpp; swap it for
any provider supported by the framework (see [PROVIDERS.md](../../agent_stem/src/startup/PROVIDERS.md)).

```
cortex/
  chat/
    prompt.py                      ← system message + pass-through input
  providers/
    default.yaml                   ← LLM backend configuration
  workflows/
    book_metadata_extraction.yaml  ← bonus: extract book metadata from a cover image
```

---

## Run locally with Docker Compose

```bash
# From the repo root — point AGENT_FOLDER at this cortex
AGENT_FOLDER=$(pwd)/examples/basic_example/cortex \
  docker compose -f agent_stem/docker-compose.default.yaml up
```

The agent is available at `http://localhost:8000`.
Interactive API docs: `http://localhost:8000/docs`.

---

## Install on Kubernetes with Helm

### Quick start (interactive, stays running)

```bash
bash scripts/k8s-install-example.sh basic_example
```

This will:
1. Start minikube (Docker driver) if not already running
2. Install the `ai-assistant` Helm chart with this cortex
3. Port-forward `:8000` (API) and `:8501` (Streamlit) to your machine
4. Block until you press **Ctrl+C**

### Manual steps

```bash
# 1. Start minikube
minikube start --driver=docker

# 2. Install the chart, passing the chat prompt inline
helm upgrade --install ai-assistant ./helm/ai-assistant \
    --set image.tag=0.1.0-dev.2 \
    --set-file cortex.chatPrompt=./examples/basic_example/cortex/chat/prompt.py \
    --wait --timeout 120s

# 3. Forward ports
kubectl port-forward --address 0.0.0.0 svc/ai-assistant-ai-assistant 8000:8000 8501:8501
```

### Supply a real LLM provider

Create a Kubernetes Secret with your API key, then reference it in the chart:

```bash
# OpenAI example
kubectl create secret generic my-llm-keys \
    --from-literal=OPENAI_API_KEY=sk-...

helm upgrade --install ai-assistant ./helm/ai-assistant \
    --set image.tag=0.1.0-dev.2 \
    --set-file cortex.chatPrompt=./examples/basic_example/cortex/chat/prompt.py \
    --set extraEnvFromSecret=my-llm-keys \
    --wait --timeout 120s
```

Your `cortex/providers/default.yaml` can then reference `${OPENAI_API_KEY}` as usual.

### Tear down

```bash
helm uninstall ai-assistant
minikube stop   # optional — skip to keep minikube warm for next run
```
