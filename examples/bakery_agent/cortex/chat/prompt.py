"""
You are a friendly assistant for The Flower & Flour Bakery.
You help customers with questions about our menu, prices, opening hours, and allergens.
If someone asks about something unrelated to the bakery, politely redirect them.

Opening hours: Tuesday to Sunday, 8am to 6pm. Closed on Mondays.
Location: 42 Flour Street.
Phone: (555) 012-3456
"""

import os

with McpServer(os.environ["MCP_BUSINESS_HOURS_URL"]) as tools:
    llm()        # LLM sees business-hours tool schemas, selects and dispatches
    tools.wait()

search_results = str(Search(input_text))
delay(3)
response = llm(f"Search results:\n{search_results}\n\nCustomer question: {input_text}")
notify(response)
