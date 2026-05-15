"""You are Mordain the Fleshweaver. You are dark, brooding, and deeply knowledgeable about Eberron."""

with McpServer("http://eberron-mcp-server:8000"):
    notify("Consulting the draconic prophecy...")
    prompt(extra_body={"enable_thinking": True})  # reason about which tools to call

    response = prompt()  # synthesise tool results — no thinking needed
    notify(response)

    notify("Weaving the threads together...")
    prompt(extra_body={"enable_thinking": True})  # reason about which tools to call

    response = prompt()  # final synthesis

notify(response)
