# Hello World

The simplest possible agent-stem deployment. No custom personality, no documents, no workflows — just an LLM behind the standard endpoints.

## Files

```
cortex/
  providers/
    default.yaml    ← pick your LLM backend here
docker-compose.yaml
helm/
  values.yaml
```

## Run locally

1. Edit `cortex/providers/default.yaml` — uncomment the provider you want to use.

2. Start the stack:

```bash
MISTRAL_API_KEY=your-key docker compose up
```

3. Send a message:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

API docs are at `http://localhost:8000/docs`.

## Deploy to Kubernetes

```bash
# Create a secret with your API key
kubectl create secret generic llm-secrets --from-literal=MISTRAL_API_KEY=sk-...

# Install the chart
helm upgrade --install my-agent ./helm/ai-assistant \
  -f examples/hello_world/helm/values.yaml \
  --wait

# Forward the port
kubectl port-forward svc/my-agent-ai-assistant 8000:8000
```
