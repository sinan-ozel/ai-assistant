- [ ] Publish to Docker Hub (Local pipeline: reformat, lint, test, publish)
- [ ] Rename the Repo
- [ ] Write a script to make sure: (1) not print in prod code (2) no imports below the top.

GOALS
- [x] (0.1.0) YAML Workflows 0.1.0
- [ ] (0.1.0) Python-as-DSL Hackable Chat
- [ ] (0.2.0) RAG
- [ ] (0.2.0) Tools
- [ ] Document Ingestion Pipeline

- [ ] (0.1.0) Helm Charts
- [ ] (0.1.0) Testing for Helm Charts
- [ ] (0.1.0) Local Run docker-compose examples

- [ ] Upgrade pytest-openapi to 0.2.2
- [x] (0.1.0) Finish logic / protocol for the default provider: if multiple custom, the one called default is default. Also: vision, large, small, default, reasoning, evaluation, coding
- [x] (0.1.0) Rename the default providers.


- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Think about how loops work
- [ ] Put in an evaluation scheme for the agent chat
- [ ] Put in the markdown ingestion
- [x] (0.1.0) Add `evaluation` to workflows.
- [ ] (0.1.0) Add an endpoint GET /private/v1/agent/system-prompt
- [ ] (0.1.0) Add an endpoint POST /private/v1/agent/conversation/{}/summary (Streaming Response)
- [ ] (0.1.0) Starting documentation: providers
- [ ] (0.1.0) Starting documentation: workflows
- [ ] (0.1.0) Starting documentation: agent chat
- [ ] (0.1.0) Starting documentation: quickstart
- [ ] (0.1.0) Starting documentation: examples
- [ ] Add thinking in the agent chat view

- [ ] Refactor: Think about the test harness. Maybe you start an environment, and test different agents on it?

- [ ] (0.1.0) Show the system prompt in streamlit
- [ ] (0.1.0) Show evaluation button & results in streamlit.
- [ ] (0.1.0) Show documentation in streamlit
- [ ] (0.1.0) Show all workflows in streamlit - Maybe a link to the OpenAPI ?
- [ ] (0.1.0) Make sure that the evaluation function is using redis-memory for storage.
- [ ] (0.1.0) Remove the "Agent Chat Interface" title on the main screen on streamlit.
