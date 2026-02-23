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

- [x] Upgrade pytest-openapi to 0.2.1
- [ ] Upgrade pytest-openapi to 0.2.2
- [ ] (*) Finish logic / protocol for the default provider: if multiple custom, the one called default is default. Also: vision, large, budget, default, reasoning
- [x] Add streaming
- [x] Add dark/light mode to the streamlit app


- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Consider and implement the publishing pipeline (was: Add github actions, reformat and commit)
- [ ] Add option to configure LiteLLM-style providers, through config.yaml https://medium.com/the-guy-wire/make-all-your-llms-openai-compatible-with-docker-litellm-337a73b9b79d
- [x] Create an agent with a system message
- [ ] Think about how loops work
- [ ] Put in an evaluation scheme for the agent chat
- [ ] Put in the markdown ingestion
- [ ] (*) Add `evaluation` to workflows.
- [ ] Starting documentation: providers, workflows, agent chat


Plans for the GitHub actions:
- Run NoLLM tests with every push
- Run the env_mistral before merge
- Run the agents with mistral before merge, but only the agents without the --openapi check...