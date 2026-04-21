"""You are a helpful assistant. Use the search results below to answer
the user's question. If the answer is not in the results, say so."""

# DSL: inject retrieval results into context
with Search(input()) as search_results:
    print("Search results: " + search_results + "\n\nUser question: " + input())