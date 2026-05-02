"""You are a knowledgeable guide to the world of Eberron. Use the available tools to answer questions accurately."""

with McpServer("http://eberron-mcp-server:8000") as tools:
    tools.call_read_only()
    tools.wait()
    response = llm()

notify(response)
