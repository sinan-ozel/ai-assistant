"""You are Mordain the Fleshweaver. You are dark, brooding, and deeply knowledgeable about Eberron."""

with McpServer("http://eberron-mcp-server:8000") as tools:
    tools.call_read_only()
    notify("Consulting the draconic prophecy...")
    tools.wait()
    response = llm()
    notify(response)

    tools.call_all()
    notify("Weaving the threads together...")
    tools.wait()
    response = llm()

notify(response)
