- [x] Publish to Docker Hub (Local pipeline: reformat, lint, test, publish)
- [x] Rename the Repo
- [ ] Write a script to make sure: (1) not print in prod code (2) no imports below the top.

GOALS
- [x] (0.1.0) YAML Workflows 0.1.0
- [x] (0.1.0) Python-as-DSL Hackable Chat
- [x] (0.1.0) RAG
- [ ] (0..0) Add MCP server
- [x] (0.1.0) Document Ingestion Pipeline

- [x] (0.1.0) Helm Charts
- [x] (0.1.0) Testing for Helm Charts
- [ ] (0.1.0) Local Run docker-compose examples



- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Think about how loops work
- [ ] (0.2.0) Markdown ingestion: may have an issue, it may rewrite the same file in deployments with multiple pods.
- [ ] (0.1.1) Update the chunking pipeline to delete files if the md does not exist, same for PDF. (Think on this: I want the markdown files to be the source of truth, but there will be a race condition if this is implemented.)
- [x] (0.1.0) Markdown ingestion: Markdown to chunking.
- [x] (0.1.0) Add `evaluation` to workflows.
- [ ] (0.1.0) Add an endpoint GET /private/v1/agent/system-prompt
- [ ] (0.1.0) Add an endpoint POST /private/v1/agent/conversation/{}/summary (Streaming Response)
- [x] (0.1.0) Starting documentation: providers
- [x] (0.1.0) Starting documentation: workflows
- [x] (0.1.0) Starting documentation: agent chat
- [x] (0.1.0) Starting documentation: quickstart
- [x] (0.1.0) Starting documentation: examples: Talk to your documents
- [ ] (0.1.1) Add thinking in the agent chat view
- [x] (0.1.0) Add a test for LanceDB chunking.
- [ ] (0.1.0) Add a test for conversation memory in non-redis environments.
- [ ] (0.1.0) Add a test for setting a keyword differently in the agent chat if it is not set.
- [x] (0.1.0) Add a test for Antropic.
- [x] (0.1.0) Simplify the Mistral environment and add it to the local tests.
- [ ] Refactor: move the env and constant assignments to one place under common
- [x] (0.1.0) Add the ability to search within specific collections. search('shelf2')
- [x] (0.1.0) Add the method library as an alias for search. Also make Search and Library aliases.
- [ ] (0.1.0) Add ability to upload image to the chat on streamlit
- [ ] (0.3.0) In workflows, if a description does not exist, fill it in from the prompt.
- [ ] (0.1.1) Add conversation summarization feature.
- [ ] Add something for either calling an LLM, or using a workflow, or both to /cortex/chat (generate? run? call? execute?)
- [ ] Add the thinking messages to /cortex/chat/prompt.py. (update_user)
- [ ] (0.1.0) Test chat evaluation in no_redis environment
- [ ] (0.1.0) Test conversation in no_redis environment
- [ ] (0.1.0) Test workflow evaluation in no_redis environment
- [x] Refactor: clean up the tests, remove unnecessary fixtures.
- [ ] (0.1.0) If there is no eval.py, disable the button on the frontend, and change the message.
- [x] (0.1.0) Remove "deploy" from streamlit
- [x] (0.1.0) Add links to OpenAPI documentation: http://localhost:8000/docs
- [x] (0.1.0) Use the books endpoint to pot something on the frontend
- [ ] (0.2.0) Extend the books endpoint, implement v2 where we see everything in the pipeline.
- [ ] (0.1.0) On the OpenAPI, categorize the endpoints as Private, Public and Workflows
- [ ] (0.1.0) Create an environment to test quick fails if the environmental variables are set incorrectly, or proper error messages.

- [ ] Add MCP testing to the test harness
- [ ] Raise error if embedding server changes.

- [ ] In the Release (Dev) Check, fail if reformatting is necessary before the tests start. Also fail if there is a stable tag that matches the current version, the current version needs to be larger.

- [ ] In the Release Check, fail if reformatting is necessary before the tests start. If the version is not greater than the last tag, fail.

- [ ] (0.1.0) Show the system prompt in streamlit
- [x] (0.1.0) Show evaluation button & results in streamlit.
- [ ] (0.1.0) Show all workflows in streamlit - Maybe a link to the OpenAPI ?

- [ ] (0.1.0) Make sure that the evaluation function is using redis-memory for storage.
- [ ] (0.1.0) Remove the "Agent Chat Interface" title on the main screen on streamlit.

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
- [ ] Refactor: Remove the generalize try ... except Exception blocks from multiple places.
- [ ] (0.1.0) Add open labels labels to the Dockerfile. Include documentation, code.
- [ ] (0.2.0) Force workflows to be streaming ndjson only.
- [ ] (0.2.0) Register workflows as MCP tools
- [ ] Give a better way to develop edit the system message dependgin on context.
- [ ] (?) Divvy-up chat.py into 01.understand_the_context.py, 02.act_on_the_problem, 03.show_the_result.
- [ ] (0.4.0) Add `ocr` as a provider, use this for OCR.
- [ ] (0.1.0) Something is weird with the tests. The conversations sizes seem to keep growing: (1) add some additinal info lines abouth the last message, and a median message. (2) Are the tests using the same conversation id? (3) How does conversation ids work?
- [ ] (0.1.0) Make sure that different conversations work on the streamlit
- [ ] (0.1.0) Make sure that different tenants work on the streamlit interface


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