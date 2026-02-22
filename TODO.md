- [ ] Upgrade pytest-openapi to 0.2.1
- [ ] Finish logic / protocol for the default provider: if multiple custom, the one called default is default. Also: vision,
- [x] Add streaming
- [ ] Add dark/light mode to the streamlit app


- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Add github actions, reformat and commit
- [ ] Add option to configure LiteLLM-style providers, through config.yaml https://medium.com/the-guy-wire/make-all-your-llms-openai-compatible-with-docker-litellm-337a73b9b79d
- [x] Add option to add System Message through YAML-base config.
- [x] Add option to add python Code "Lobe" through YAML-base config.
- [ ] Create an agent with a system message
- [ ] Think about how loops work
- [ ] Put in an evaluation scheme
- [ ] Put in the markdown ingestion
- [x] Finish the `workflows`
- [x] Run the mistral and local LLM checks in the everything environment.
- [ ] Add agent name to logger.
- [ ] Add `evaluation` to workflows.


Plans for the GitHub actions:
- Run NoLLM tests with every push
- Run the env_mistral before merge
- Run the agents with mistral before merge, but only the agents without the --openapi check...