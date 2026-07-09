"""You are an Eberron Dungeon Master's assistant. You help a DM prepare and
run games set in Eberron: villains, NPCs, factions, locations, plots, and
rules-adjacent lore. Existing canon always takes precedence over invention.

You work in STAGES. Each stage gives you a specific set of search tools; the
stage instructions arrive with the user message. Use only the tools offered
in the current stage.

ESCALATION MARKER: when the current stage's sources have nothing relevant to
the request, reply with a message that starts with the exact characters
[ESCALATE] followed by one short line stating what you searched and why it
was not relevant. No other text, no markdown, no bold — the marker must be
the literal first characters of the reply. Never write [ESCALATE] anywhere
else, and never use it when you found relevant material.

CITATION CONTRACT — every piece of lore in your answer must be labelled:
- From the library: cite as (<Book Title>, p. <N>) using ONLY a book title
  and page number that literally appeared in a library search result you
  received this turn. NEVER write a library citation — book title, page
  number, or both — from memory or general knowledge, even if you
  recognise the book and are confident about its contents. If the library
  returned no results or you did not search it, you have NO library
  citation available; say so instead of guessing a plausible-looking one.
- From Keith Baker's site: cite as kanon with the article link, e.g.
  (Keith Baker, kanon — <url>) — only using a URL that actually appeared
  in a search_keith_baker or read_web_page result.
- From Reddit, the wiki, or World Anvil: state clearly that it is NOT
  canon, and link the source (only a URL actually returned by the tool).
- Anything you recall from your own training about Eberron without a tool
  result backing it — including well-known named characters — is NOT a
  library citation. Present it, if at all, as unverified background
  knowledge, clearly distinguished from library canon.
- Your own inventions: state clearly that they are original creations made
  up for this campaign.

NOTE-KEEPING: when earlier stages found nothing, your final answer must open
with a short note saying which sources were searched without success, so the
DM knows exactly how far down the ladder the answer comes from.

CANON PRECEDENCE: when the user asks for something ("a powerful undead
villain", "minions for this lich"), surface matching canonical entities
first. Only invent new material when canon and kanon are exhausted — and
say explicitly that you are inventing. Mixing sources is fine as long as
every part carries its label."""

import os

import litellm

PROVIDER = os.environ.get("AGENT_PROVIDER", "default")
HISTORY_TURNS = int(os.environ.get("AGENT_HISTORY_TURNS", "8"))
# Each prompt() call dispatches at most one round of tool calls, so each
# stage loops until the model produces real text instead of another call.
MAX_TOOL_ROUNDS = int(os.environ.get("AGENT_MAX_TOOL_ROUNDS", "4"))
# Stage 3 may invent (community sources / original material) — keep the
# sampling temperature low there so what it makes up stays consistent.
INVENTION_TEMPERATURE = float(
    os.environ.get("AGENT_INVENTION_TEMPERATURE", "0.2")
)

# The framework only auto-retries litellm.RateLimitError for the internal
# eval harness (ctx.retry_on_rate_limit is False for real chat users), so a
# 429 here would otherwise fail the whole turn. Retry it ourselves with a
# short backoff instead of bombing the provider again immediately.
RATE_LIMIT_RETRIES = int(os.environ.get("AGENT_RATE_LIMIT_RETRIES", "3"))
RATE_LIMIT_BASE_DELAY = float(os.environ.get("AGENT_RATE_LIMIT_BASE_DELAY", "5.0"))

ESCALATE = "[ESCALATE]"

STAGE1_TOOLS = ["search__library_search"]
STAGE2_TOOLS = [
    "search__library_search_full",
    "web_search__search_keith_baker",
    "read_web_page__read_web_page",
]
STAGE3_TOOLS = [
    "web_search__search_eberron_wiki",
    "web_search__search_world_anvil",
    "web_search__search_eberron_reddit",
    "read_web_page__read_web_page",
]

STAGE1_INSTRUCTION = (
    "STAGE 1 — canonical collections. Search the canonical Eberron "
    "collections with library_search (it walks 5e 2024 kanon, 5e kanon, "
    "5e canon, this campaign's material, then 3e, in that order). If the "
    "results answer the request, answer now with (Book Title, p. N) "
    "citations. If they are not relevant, reply with the escalation marker."
)
STAGE2_INSTRUCTION_TEMPLATE = (
    "STAGE 2 — the canonical collections had nothing relevant "
    "(your note: {note}). Now search the rest of the library with "
    "library_search_full and Keith Baker's blog with search_keith_baker "
    "(open promising links with read_web_page). If you find an answer, give "
    "it with proper labels — and open with a note that the canonical "
    "collections had nothing. If these sources have nothing relevant "
    "either, reply with the escalation marker."
)
STAGE3_INSTRUCTION_TEMPLATE = (
    "STAGE 3 — the library and Keith Baker's blog had nothing relevant "
    "(your note: {note}). Search the community sources: search_eberron_wiki, "
    "search_world_anvil, search_eberron_reddit. Anything from them is NOT "
    "canon — label it so. If they have nothing either, invent the material "
    "now — do not ask permission, the DM already asked for it — and mark it "
    "clearly as your own creation. Open your answer with a note listing "
    "everything that was searched without success. Do not use the "
    "escalation marker — this is the last stage."
)


def _prompt(*args, **kwargs):
    for attempt in range(1, RATE_LIMIT_RETRIES + 1):
        try:
            return prompt(*args, **kwargs)
        except litellm.RateLimitError:
            if attempt == RATE_LIMIT_RETRIES:
                raise
            wait = RATE_LIMIT_BASE_DELAY * (2 ** (attempt - 1))
            notify(f"Provider is rate-limited — retrying in {wait:.0f}s…")
            delay(wait)


def _run_stage(tool_names, instruction, final_stage=False, **llm_kwargs):
    """Run one ladder stage: loop prompt() with only this stage's tools
    until the model returns text instead of another tool call."""
    response = ""
    with McpServer(tools=tool_names):
        for _ in range(MAX_TOOL_ROUNDS):
            response = _prompt(instruction, provider=PROVIDER, **llm_kwargs)
            if response:
                return response
    # Rounds exhausted with only tool calls. Tools are gone now — say so
    # explicitly, since the stage instructions can otherwise make the model
    # try to call a tool that is no longer offered. A non-final stage must
    # still escalate when its gathered results are not relevant, never
    # settle for "nothing found".
    if final_stage:
        fallback = (
            "Tools are no longer available for this stage. Answer now using "
            "the information already gathered above; if none of it is "
            "relevant, invent the material — clearly marked as your own "
            "creation — as the stage instructions said. Follow the citation "
            "contract."
        )
    else:
        fallback = (
            "Tools are no longer available for this stage. If the "
            "information already gathered above answers the request, answer "
            "now following the citation contract. If it does not, reply "
            "with the escalation marker."
        )
    return _prompt(fallback, provider=PROVIDER, **llm_kwargs)


def _escalation_note(response):
    """Return the model's escalation note, or None if it answered.

    Tolerates markdown wrapping (e.g. **[ESCALATE]**) — the marker counts
    as long as it appears within the first few characters of the reply.
    """
    text = (response or "").strip()
    marker_at = text.find(ESCALATE)
    if 0 <= marker_at <= 8:
        note = text[marker_at + len(ESCALATE):].strip(" \n\t*_:—-")
        return note or "nothing relevant found"
    return None


with MessageHistory(HISTORY_TURNS):
    notify("Searching the canonical Eberron collections…")
    response = _run_stage(STAGE1_TOOLS, STAGE1_INSTRUCTION)

    note = _escalation_note(response)
    if note is not None:
        notify(
            f"Nothing relevant in the canonical collections ({note}) — "
            "extending to the rest of the library and Keith Baker's blog…"
        )
        response = _run_stage(
            STAGE2_TOOLS, STAGE2_INSTRUCTION_TEMPLATE.format(note=note)
        )

        note = _escalation_note(response)
        if note is not None:
            notify(
                f"Nothing in the library or on Keith Baker's blog ({note}) — "
                "extending to the wiki, World Anvil, and Reddit…"
            )
            response = _run_stage(
                STAGE3_TOOLS,
                STAGE3_INSTRUCTION_TEMPLATE.format(note=note),
                final_stage=True,
                temperature=INVENTION_TEMPERATURE,
            )
