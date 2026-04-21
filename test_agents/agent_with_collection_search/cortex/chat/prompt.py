"""You are a helpful assistant. Answer based only on the search results provided below."""

with Search(input(), "shelf1") as results:
    print(results)
    print("User question: " + input())
