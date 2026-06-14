"""You are Mordain the Fleshweaver. You are dark, brooding, and deeply knowledgeable about Eberron."""

with McpServer("http://eberron-mcp-server:8000"):
    notify("Consulting the draconic prophecy...")
    prompt(extra_body={"enable_thinking": True})  # reason about which tools to call

    response = prompt(tool_choice="none")  # synthesise tool results — force text, no more tool calls
    notify(response)

    notify("Weaving the threads together...")
    prompt(extra_body={"enable_thinking": True})  # reason about which tools to call

    response = prompt(tool_choice="none")  # final synthesis — force text

notify(response)
