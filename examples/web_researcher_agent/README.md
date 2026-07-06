# Web Researcher Agent (ARIA)

A research assistant that combines two local MCP tools: a Google Scholar
search (via the Serper API) and a real-time clock. Demonstrates how to ship
custom Python tools inside the cortex under `mcp/tools/` — no separate tool
server required.

## Files

```
cortex/
  providers/
    default.yaml        ← Mistral API
  chat/
    prompt.py           ← system message + McpServer() tool phase
  mcp/
    tools/
      google_scholar.py ← Google Scholar search via Serper (SERPER_API_KEY)
      time_tool.py      ← current date/time in a given IANA timezone
docker-compose.yaml
helm/
  values.yaml
```

## Run locally

```bash
MISTRAL_API_KEY=your-key SERPER_API_KEY=your-key docker compose up
```

Then try it:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find recent papers on prompt caching for LLM inference."}'
```

API docs at `http://localhost:8000/docs`.

## Notes

- `SERPER_API_KEY` comes from [serper.dev](https://serper.dev); the free tier
  is enough to try the example.
- The time tool needs no credentials — asking "What time is it in London?"
  exercises the full local-MCP-tool path without any external API.
