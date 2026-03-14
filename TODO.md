- [ ] Publish to Docker Hub (Local pipeline: reformat, lint, test, publish)
- [ ] Rename the Repo
- [ ] Write a script to make sure: (1) not print in prod code (2) no imports below the top.

GOALS
- [x] (0.1.0) YAML Workflows 0.1.0
- [ ] (0.1.0) Python-as-DSL Hackable Chat
- [ ] (0.1.0) RAG
- [ ] (0.2.0) Tools
- [ ] (0.1.0) Document Ingestion Pipeline

- [ ] (0.1.0) Helm Charts
- [ ] (0.1.0) Testing for Helm Charts
- [ ] (0.1.0) Local Run docker-compose examples

- [x] Upgrade pytest-openapi to 0.2.2
- [x] (0.1.0) Finish logic / protocol for the default provider: if multiple custom, the one called default is default. Also: vision, large, small, default, reasoning, evaluation, coding
- [x] (0.1.0) Rename the default providers.


- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Think about how loops work
- [ ] (0.1.0) Put in an evaluation scheme for the agent chat
- [x] (0.1.0) Put in the markdown ingestion
- [ ] (0.1.0) Markdown ingestion: has an issue, it will rewrite the same file in deployments with multiple pods.
- [x] (0.1.0) Markdown ingestion: Markdown to chunking.
- [x] (0.1.0) Add `evaluation` to workflows.
- [ ] (0.1.0) Add an endpoint GET /private/v1/agent/system-prompt
- [ ] (0.1.0) Add an endpoint POST /private/v1/agent/conversation/{}/summary (Streaming Response)
- [ ] (0.1.0) Starting documentation: providers
- [ ] (0.1.0) Starting documentation: workflows
- [ ] (0.1.0) Starting documentation: agent chat
- [ ] (0.1.0) Starting documentation: quickstart
- [ ] (0.1.0) Starting documentation: examples
- [ ] Add thinking in the agent chat view
- [ ] (0.1.0) Add a test for LanceDB chunking.
- [ ] (0.1.0) Add a test for conversation memory in non-redis environments.
- [ ] (0.1.0) Add a test for Antropic.
- [ ] (0.1.0) Simplify the Mistral environment and add it to the local tests.

- [ ] Refactor: Think about the test harness. Maybe you start an environment, and test different agents on it?
- [ ] Test Harness: Do not use the everything environment for agents, just use the no_llm environment
- [ ] Test Harness: Add some "bad" agents to see that they crash.
- [ ] Test Harness: Add the Mistral environment back in - also to test no providers set case.

- [ ] (0.1.0) Show the system prompt in streamlit
- [ ] (0.1.0) Show evaluation button & results in streamlit.
- [ ] (0.1.0) Show documentation in streamlit /private/v1/books/{} (Lists chunk count, book metadata)
- [ ] (0.1.1) Show documentation in streamlit /private/v1/books/{}/search (Lists chunk count, book metadata)
- [ ] (0.1.0) Show all workflows in streamlit - Maybe a link to the OpenAPI ?

- [ ] (0.1.0) Make sure that the evaluation function is using redis-memory for storage.
- [ ] (0.1.0) Remove the "Agent Chat Interface" title on the main screen on streamlit.

- [ ] I am still seeing a message like this? tests-runner-self-hosted-llm  | .::test_openapi[POST /v1/api/generate [generated-10]] <- ../usr/local/lib/python3.12/site-packages/pytest_openapi/plugin.py PASSED [ 66%]  Request: {"model": "Lorem ipsum dolor sit amet", "prompt": ...
tests-runner-self-hosted-llm  |   Expected [200]: {"model": "gemma3:4b", "created_at": "2024-12-20T0...
tests-runner-self-hosted-llm  |   Actual [501]: {"detail": "Streaming not yet implemented"}

- [ ] Grafana integration
- [ ] Use a language model to get a PDF language rather than OCR_LANGUAGE environmenyal variable
- [ ] Make chunking hackable (?)
- [ ] Compare the chunk sizes, warn about largest chunks, suggest model and VRAM size.
- [ ] Improve chunking: detect tables, refactor the chunking library, place tests.