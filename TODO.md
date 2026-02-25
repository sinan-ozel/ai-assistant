- [ ] Publish to Docker Hub (Local pipeline: reformat, lint, test, publish)
- [ ] Rename the Repo
- [ ] Write a script to make sure: (1) not print in prod code (2) no imports below the top.

GOALS
- [ ] (*) YAML Workflows 0.1.0
- [ ] Python-as-DSL Hackable Chat
- [ ] RAG
- [ ] Tools
- [ ] Document Ingestion Pipeline

- [ ] Helm Charts
- [ ] Testing for Helm Charts
- [ ] (*) Local Run docker-compose examples

- [ ] Upgrade pytest-openapi to 0.2.2
- [ ] (*) Finish logic / protocol for the default provider: if multiple custom, the one called default is default. Also: vision, large, small, default, reasoning, evaluation, coding
- [ ] (*) Rename the default providers.


- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Think about how loops work
- [ ] Put in an evaluation scheme for the agent chat
- [ ] Put in the markdown ingestion
- [ ] (*) Add `evaluation` to workflows.
- [ ] Add an endpoint GET /private/v1/agent/system-prompt
- [ ] Add an endpoint POST /private/v1/agent/conversation/{}/summary (Streaming Response)
- [ ] (*) Starting documentation: providers, workflows, agent chat

- [ ] Refactor: Think about the test harness. Maybe you start an environment, and test different agents on it?

5