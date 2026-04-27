# Bakery Agent

A customer-facing chat assistant for a fictional bakery, used as the introductory
example in the docs. The agent knows the menu and allergen guide via RAG and has
a fixed personality defined in its system message.

## Files

```
cortex/
  providers/
    default.yaml        ← Mistral API
  chat/
    prompt.py           ← system message + document search
  library/
    menu.md             ← bakery menu (replace with a PDF if you prefer)
    allergen-guide.md   ← allergen information
docker-compose.yaml
helm/
  values.yaml
```

## Run locally

```bash
MISTRAL_API_KEY=your-key docker compose up
```

Then try it:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you have anything vegan?"}'
```

API docs at `http://localhost:8000/docs`.

## Notes

- `menu.md` and `allergen-guide.md` are indexed automatically at startup.
  Replace them with real PDFs if preferred — the pipeline handles both.
- The library files are fictional. Edit them to reflect your real menu.

## Deploy to Kubernetes

```bash
kubectl create secret generic llm-secrets --from-literal=MISTRAL_API_KEY=sk-...

helm upgrade --install bakery ./helm/ai-assistant \
  -f examples/bakery_agent/helm/values.yaml \
  --wait

kubectl port-forward svc/bakery-ai-assistant 8000:8000
```
