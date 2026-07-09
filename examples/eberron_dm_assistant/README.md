# Eberron DM Assistant

A Dungeon Master's assistant for the world of Eberron. It answers lore
questions and creative requests ("create me a powerful undead villain")
by walking a strict three-stage source ladder, notifies the DM whenever a
stage comes up empty, and labels every piece of lore with where it came
from.

## The three stages

The ladder is **script-driven**: each stage runs with only its own tools
registered (the `McpServer(tools=[...])` filter), so the model cannot skip
ahead. When a stage's sources have nothing relevant, the model replies with
an `[ESCALATE]` marker plus a one-line note; the script relays that note to
the DM via a notification and moves to the next stage.

| Stage | Sources | Tools | Label in answers |
|---|---|---|---|
| 1 | Canonical collections, in priority order: `eberron_5e24_kanon`, `eberron_5e_kanon`, `eberron_5e_canon`, `my_eberron`, then `eberron_3e` | `library_search` | `(Book Title, p. N)` |
| 2 | Rest of the library + keith-baker.com | `library_search_full`, `search_keith_baker`, `read_web_page` | `(Book Title, p. N)` / `(Keith Baker, kanon — <url>)` |
| 3 | eberron.fandom.com, World Anvil, r/Eberron — and, failing those, original invention | `search_eberron_wiki`, `search_world_anvil`, `search_eberron_reddit`, `read_web_page` | NOT canon with link / explicitly marked as original |

Stage 3 is the only stage where invention is allowed, so its LLM calls run
at a low sampling temperature (`AGENT_INVENTION_TEMPERATURE`, default
`0.2`) to keep the made-up material consistent. The final answer must open
with a note listing which sources were searched without success.

Within stage 1, `library_search` walks the canonical collections one tag at
a time and stops at the first collection with a strong match (relevance
score ≥ `LIBRARY_STRONG_MATCH_SCORE`, default `0.5`); `eberron_3e` is
consulted only when the four primary tags have no strong match. The tag
lists are `LIBRARY_TAGS_PRIMARY` and `LIBRARY_TAGS_FALLBACK`.

## Files

```
cortex/
  providers/
    default.yaml        ← Mistral (large context — recommended)
    local.yaml          ← external llama.cpp gemma4:e2b (${LLAMA_CPP_HOST})
  chat/
    prompt.py           ← the staged ladder: per-stage tool scoping,
                          [ESCALATE] marker handling, DM notifications,
                          low-temperature stage 3, backoff on rate limits
  mcp/
    tools/
      search.py         ← canonical tag ladder + full-library search via the
                          agent's /private/v1/search; book + page per
                          passage, STRONG/weak labels. Shadows the
                          framework's default library tool. Swap point for a
                          future graph-retrieval service.
      web_search.py     ← 4 site-scoped SerpApi searches (SERPAPI_API_KEY)
      read_web_page.py  ← fetch + strip a page when a snippet is not enough
  library/              ← create this and drop official Eberron PDFs in it
docker-compose.yaml
helm/
  values.yaml
```

## The library

Put your Eberron book PDFs under `cortex/library/`, in folders named after
the canonical tags:

```
cortex/library/
  eberron_5e24_kanon/   ← 5e 2024 kanon
  eberron_5e_kanon/     ← 5e kanon
  eberron_5e_canon/     ← 5e official canon
  my_eberron/           ← this campaign's own material
  eberron_3e/           ← 3e/3.5e books (fallback within stage 1)
  <anything else>/      ← searched only in stage 2 (library_search_full)
```

Folder names become book tags (any nesting level works for the tag filter).
Books are converted and chunked at startup — check progress at
`GET /private/v1/books`. Page-number extraction reads printed page footers
from the PDF, so citations use the book's own page numbering.

**Note:** the tag filter requires Qdrant (the compose file and Helm chart
both run it). The LanceDB fallback cannot filter on tags, so without Qdrant
stage 1 finds nothing and everything escalates.

## Run locally

```bash
MISTRAL_API_KEY=your-key SERPAPI_API_KEY=your-key docker compose up
```

Then try it:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create me a powerful undead villain.", "conversation_id": "prep-session-1"}'
```

Expected behaviour: stage 1 surfaces the canonical answer (Lady Illmarrow,
with book + page) before anything else is consulted. Follow-up turns in the
same `conversation_id` ("now give me her minions") walk the ladder again —
canon minions first, then clearly labelled web finds or inventions.

## Switching to the small local model

To exercise small-context behaviour, point `local.yaml` at a llama.cpp
server and select it per deployment:

```bash
LLAMA_CPP_HOST=http://<host>:8080/v1 AGENT_PROVIDER=local \
MISTRAL_API_KEY=your-key SERPAPI_API_KEY=your-key \
AGENT_HISTORY_TURNS=3 docker compose up
```

- `AGENT_PROVIDER` selects the provider YAML (`default` = Mistral,
  `local` = gemma4:e2b) for every LLM call in `prompt.py`.
- `AGENT_HISTORY_TURNS` bounds how many past turn pairs the model sees
  (`MessageHistory`); lower it for small context windows.
- If `LLAMA_CPP_HOST` is unset, the `local` provider fails validation at
  startup with a logged warning and is simply unavailable — Mistral still
  works.

## Deploy with Helm

```bash
kubectl create secret generic ai-assistant-api-keys \
  --from-literal=MISTRAL_API_KEY=... \
  --from-literal=SERPAPI_API_KEY=...

helm upgrade --install eberron-dm \
  oci://registry-1.docker.io/sinanozel/ai-assistant-helm \
  --version <released-version> \
  -f helm/values.yaml
```

`helm/values.yaml` mounts the cortex from a host path and injects the
secret via `extraEnvFromSecret`. To use the `local` provider in-cluster,
uncomment `LLAMA_CPP_HOST` under `extraEnv` (the chart only sets that
variable itself when it runs its own `llamacpp` deployment).

## Notes

- **Requires the `tools=` filter on `McpServer`** (per-stage tool scoping),
  which is newer than image `0.1.1-dev.20` — run against an image built
  from current `agent_stem` source, or the next dev release.
- `SERPAPI_API_KEY` comes from [serpapi.com](https://serpapi.com) — note
  this is **SerpApi**, not the similarly-named Serper (serper.dev); the two
  are different services with incompatible keys. Without it the web tools
  report themselves unavailable.
- World Anvil search is scoped with `site:worldanvil.com eberron <query>`;
  Google's index of World Anvil is shallow, so expect thinner results
  there than from the wiki.
- `prompt.py` retries on a Mistral/provider rate limit (429) with a short
  backoff before giving up — the framework's own rate-limit retry is
  reserved for the internal eval harness, so a real chat session would
  otherwise fail the turn outright on a transient 429. Tune with
  `AGENT_RATE_LIMIT_RETRIES` / `AGENT_RATE_LIMIT_BASE_DELAY`.
