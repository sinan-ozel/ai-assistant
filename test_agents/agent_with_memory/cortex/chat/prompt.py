"""You are a helpful assistant. Remember everything the user tells you."""

with MessageHistory(10):
    response = prompt()
