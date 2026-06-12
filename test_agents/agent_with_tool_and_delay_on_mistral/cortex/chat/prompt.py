"""You are a knowledgeable guide to the world of Eberron and a helpful assistant. Use the available tools to answer questions accurately."""

with McpServer(["http://eberron-mcp-server:8000", "http://localhost:8001"]):
    prompt()
    delay(5)

response = prompt()
