- [x] Publish to Docker Hub (Local pipeline: reformat, lint, test, publish)
- [x] Rename the Repo
- [ ] Write a script to make sure: (1) not print in prod code (2) no imports below the top.
- [x] Check out how orchestration works at Claude Code.

GOALS
- [x] (0.1.0) YAML Workflows 0.1.0
- [x] (0.1.0) Python-as-DSL Hackable Chat
- [x] (0.1.0) RAG
- [x] (0.1.0) Add MCP server
- [x] (0.1.0) Document Ingestion Pipeline

- [x] (0.1.0) Helm Charts
- [x] (0.1.0) Testing for Helm Charts
- [x] (0.1.0) Local Run docker-compose examples


- [x] (0.1.0) Add eval to the bakery example


- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] (0.2.0) Markdown ingestion: may have an issue, it may rewrite the same file in deployments with multiple pods.
- [ ] (0.1.1) Update the chunking pipeline to delete files if the md does not exist, same for PDF. (Think on this: I want the markdown files to be the source of truth, but there will be a race condition if this is implemented.)
- [ ] (0.1.0) Add an endpoint GET /private/v1/agent/system-prompt
- [ ] (0.1.0) Add an endpoint POST /private/v1/agent/conversation/{}/summary (Streaming Response)
- [ ] (0.1.1) Add thinking in the agent chat view
- [ ] (0.1.0) Add a test for setting a keyword differently in the agent chat if it is not set.
- [ ] Refactor: move the env and constant assignments to one place under common
- [x] (0.1.0) Add ability to upload image to the chat on streamlit
- [ ] (0.3.0) In workflows, if a description does not exist, fill it in from the prompt.
- [ ] (0.1.1) Add conversation summarization feature.
- [x] Add something for either calling an LLM, or using a workflow, or both to /cortex/chat (generate? run? call? execute?)
- [ ] Add the thinking messages to /cortex/chat/prompt.py. (update_user)
- [ ] (0.1.0) Test chat evaluation in no_redis environment
- [ ] (0.1.0) Test conversation in no_redis environment
- [ ] (0.1.0) Test workflow evaluation in no_redis environment
- [ ] (0.1.0) If there is no eval.py, disable the button on the frontend, and change the message.
- [ ] (0.2.0) Extend the books endpoint, implement v2 where we see everything in the pipeline.
- [ ] (0.1.0) Create an environment to test quick fails if the environmental variables are set incorrectly, or proper error messages.
- [ ] (0.1.1) Ability to add books and create shelves on the interface.
- [ ] (0.1.0) Make sure that execute_prompt_script in agent_stem/src/common/prompt_dsl.py is removing duplicate messages, if `message_history` becomes editable.

- [ ] In the logs, make sure that this kind of message is being truncated properly:
app-test-no-qdrant        | INFO:endpoints.agent_chat:Agent chat: Last message (user): {'role': 'user', 'content': [{'type': 'text', 'text': 'Describe what you see in this image in one sentence.'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,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

- [ ] (0.1.0) Log a warning every time the context window is not enough. Add to /metrics
- [ ] Introspect execute_prompt_script in agent_stem/src/common/prompt_dsl.py and make sure that docstring has all the core primitives. Then also check the docstring against the documentation and find out if anything is missing.

- [ ] (0.2.0) Switch to synced-memory
- [x] (0.1.0) Add eval to bakery example

- [ ] (0.1.1) Add chunk information to the interface.

- [ ] Refactor: under each agent, write the tests that they need to run with each environment: tests/ --> tests/default, tests/no_qdrant, tests/no_mcp

- [ ] Add MCP testing to the test harness
- [ ] (0.1.1) Raise error if embedding server changes.

- [x] In the Release (Dev) Check, fail if reformatting is necessary before the tests start. Also fail if there is a stable tag that matches the current version, the current version needs to be larger.

- [ ] In the Release Check, fail if reformatting is necessary before the tests start. If the version is not greater than the last tag, fail.

- [ ] (0.1.0) Show the system prompt in streamlit
- [x] (0.1.0) Show all workflows in streamlit - Maybe a link to the OpenAPI ?

- [ ] (0.1.0) Make sure that the evaluation function is using redis-memory for storage.

- [ ] (0.3.0) Add L1 and cosine distance as metrics.
- [ ] Refactor: move default_providers global from under api.py to somewher reasonable under common

- [ ] Implement streaming in the generation API. I am still seeing a message like this? tests-runner-self-hosted-llm  | .::test_openapi[POST /v1/api/generate [generated-10]] <- ../usr/local/lib/python3.12/site-packages/pytest_openapi/plugin.py PASSED [ 66%]  Request: {"model": "Lorem ipsum dolor sit amet", "prompt": ...
tests-runner-self-hosted-llm  |   Expected [200]: {"model": "gemma3:4b", "created_at": "2024-12-20T0...
tests-runner-self-hosted-llm  |   Actual [501]: {"detail": "Streaming not yet implemented"}

- [ ] Grafana integration
- [ ] Use a language model to get a PDF language rather than OCR_LANGUAGE environmental variable
- [ ] Make chunking hackable (?)
- [ ] Compare the chunk sizes, warn about largest chunks, suggest model and VRAM size.
- [ ] Improve chunking: detect tables, refactor the chunking library, place tests.
- [ ] (0.3.0) Add custom embedding provider. Remove EMBEDDING_HOST from env in the test environments, and remove the servers.
- [ ] (0.1.0) Change the test in no_qdrant environment to use the endpoints.
- [x] Refactor: Remove the generalize try ... except Exception blocks from multiple places.
- [ ] (0.1.0) Add open labels to the Dockerfile. Include documentation, code.
- [ ] (0.2.0) Force workflows to be streaming ndjson only.
- [ ] (0.2.0) Register workflows as MCP tools
- [ ] Give a better way to develop edit the system message dependgin on context.
- [ ] (0.4.0) Add `ocr` as a provider, use this for OCR.
- [ ] (0.1.0) Something is weird with the tests. The conversations sizes seem to keep growing: (1) add some additinal info lines abouth the last message, and a median message. (2) Are the tests using the same conversation id? (3) How does conversation ids work?
- [ ] (0.1.0) Make sure that different conversations work on the streamlit
- [ ] (0.1.0) Make sure that different tenants work on the streamlit interface
- [ ] If the embedding server or mode changes, rerun the chunking, log a warning.

- [ ] Bug: See the following, this is a problem. The model is missing from the server, but we got a non-descript 400 error.
tests-runner-default    |     def test_nutrition_information_extraction():
tests-runner-default    |         """Test nutrition information extraction from food label image."""
tests-runner-default    |         image_path = IMAGES_DIR / "IMG_B768CE83-9FEC-461A-BE63-CDDF64EBEB58.jpeg"
tests-runner-default    |         image_base64 = get_image_base64(image_path)
tests-runner-default    |         url = f"{BASE_URL}/v1/extract-nutrition-information"
tests-runner-default    |
tests-runner-default    |         response = requests.post(
tests-runner-default    |             url,
tests-runner-default    |             json={
tests-runner-default    |                 "messages": [
tests-runner-default    |                     {
tests-runner-default    |                         "role": "user",
tests-runner-default    |                         "content": [
tests-runner-default    |                             {
tests-runner-default    |                                 "type": "image_url",
tests-runner-default    |                                 "image_url": {
tests-runner-default    |                                     "url": f"data:image/jpeg;base64,{image_base64}"
tests-runner-default    |                                 },
tests-runner-default    |                             }
tests-runner-default    |                         ],
tests-runner-default    |                     }
tests-runner-default    |                 ],
tests-runner-default    |                 "temperature": 0.0,
tests-runner-default    |                 "max_tokens": 500,
tests-runner-default    |             },
tests-runner-default    |             timeout=300,  # Must be longer than provider timeout (150s) + buffer
tests-runner-default    |         )
tests-runner-default    |
tests-runner-default    |         print(response.content)
tests-runner-default    |
tests-runner-default    | >       assert response.status_code == 200
tests-runner-default    | E       assert 400 == 200
tests-runner-default    | E        +  where 400 = <Response [400]>.status_code
tests-runner-default    |
tests-runner-default    | test_image_workflows.py:55: AssertionError
tests-runner-default    | ----------------------------- Captured stdout call -----------------------------
tests-runner-default    | b'{"detail":{"error":"LLM returned invalid JSON: Expecting value: line 1 column 1 (char 0)","llm_response":""}}'


# Documentation Notes:

## Workflows

## Chat

## Retrieval

How to add books or documents i.e. "corpus". (Under the `library/` folder.) Use further folders as collections.

Library: Either use PDFs with correct textual content, or there may be an OCR fallback. If the OCR fallback takes place, it has to be English.

PDF files are the source of truth, delete or update as they go along.

Usage: lancedb only, but ephemeral. Qdrant without a volume locally is another option. qdrant for prod.

(*) Markdown ingestion: has an issue, it will rewrite the same file in deployments with multiple pods.


## Hobby Usage

## Development Usage

## Production Usage
