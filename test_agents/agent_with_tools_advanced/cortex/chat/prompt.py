"""You are Mordain the Fleshweaver. You are dark, brooding, and deeply knowledgeable about Eberron."""

with McpServer("http://eberron-mcp-server:8000"):
    notify("Consulting the draconic prophecy...")
    prompt()

    response = prompt()
    notify(response)

    notify("Weaving the threads together...")
    prompt()

    response = prompt()

notify(response)
