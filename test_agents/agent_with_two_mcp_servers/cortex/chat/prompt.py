"""You are a helpful assistant with access to multiple tool servers. Use the available tools to answer questions accurately."""

with McpServer(), McpServer("http://eberron-mcp-server:8000"):
    prompt()

response = prompt()
