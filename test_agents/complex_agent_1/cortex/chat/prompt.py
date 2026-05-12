"""You are a Dungeon Master assistant for an Eberron campaign. You have deep
knowledge of Eberron lore, factions, geography, and NPCs. Use the search
results below to answer questions about the campaign world. If the answer
is not in the results, draw on your general Eberron knowledge and say so."""

# Step 1: Extract search terms — proper nouns and general topic keywords.
# Uses the provider default temperature (0.3) for focused, deterministic output.
search_terms = prompt(
    f"Extract the best search terms for this Eberron campaign question.\n"
    f"Include proper nouns (people, places, factions, artefacts) and general "
    f"topic keywords that cover the full scope of what is being asked.\n"
    f"Return only a short comma-separated list of terms — no explanation.\n\n"
    f"Question: {input_text}"
)

# Step 2: Classify intent — 1 = retrieve existing lore, 10 = create something new.
score_text = prompt(
    f"On a scale of 1 to 10, is this question asking to create something new (10) "
    f"or to find information about something that already exists in the world (1)?\n"
    f"Reply with a single integer only.\n\n"
    f"Question: {input_text}",
    provider="default",
)
import re as _re
_m = _re.search(r"\d+", score_text)
score = max(1, min(10, int(_m.group()) if _m else 5))

# 1 → 0.1 (tight, factual retrieval), 10 → 0.9 (open, creative generation)
temperature = round(0.1 + (score - 1) * (0.8 / 9), 2)

# Step 3: Final answer — inject search results via ctx, temperature overrides provider default.
with Search(search_terms):
    response = prompt(temperature=temperature)