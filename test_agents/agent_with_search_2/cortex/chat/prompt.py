"""You are a helpful assistant. Use the search results below to answer
the user's question. If the answer is not in the results, say so."""

# DSL: inject retrieval results into context
results = Search(input_text)
print(results)
print("User question: " + input_text)