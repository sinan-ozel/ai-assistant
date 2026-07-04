- [x] Write a script to make sure: (1) not print in prod code (2) no imports below the top.
      (lint/check_no_print.py covers prints; ruff PLC0415 covers imports.)


0.1.0
- [x] Fix thread-safety bug in prompt_dsl.py: `contextlib.redirect_stdout` is
      process-wide, but `_run_interactive_script` runs in executor threads —
      two concurrent /v1/agent/chat requests can capture each other's print()
      output. Fix: inject a per-request `print` into the DSL globals (same
      pattern as the `input` override) and drop the redirect.
- [x] Document the cortex trust boundary: whoever can edit the cortex
      (ConfigMap in k8s) executes arbitrary Python in the pod. State
      explicitly in docs that cortex changes need code-level review and RBAC.
      (README, "The cortex is your application" section.)
- [x] Chat window: multple conversations,
- [ ] Chat window should increase in height as the browser window changes?
- [ ] Make sure that different tenants work on the streamlit interface
- [ ] The title, "Agent Chat", needs to be customizable.
- [x] Turn the search into a full MCP toolset.
  - [ ] Add L1 and cosine distance as metrics.
- [ ] Should implement 413 - prompt too long
- [x] Make streamlit front-end streaming.
- [x] Add the medical literature agent to the examples.
- [x] Create new test environment based on default, called api_test (for workflows) and mcp_test (for just the search for now). Maybe together?
- [x] Add a test with an additional tool.
- [ ] Use the resources and limits from the helm chart template in the testing docker compose files.


0.1.1
- [ ] Add dedicated test coverage around the sync↔async bridge (DSL script
      runs sync in an executor thread, bridges back to the event loop for
      streaming LLM calls via DslRunContext.event_loop). This is the most
      fragile seam — cover concurrent requests, streaming + tools, and
      mid-stream errors.
- [ ] Add chunk information to the interface.
- [x] Raise error if embedding server changes.
- [ ] Add useful tools, current time, etc..
- [ ] Very basic multi-agent support

Upgrade to Gemma4
- [ ] test_agents/agent_with_incorrect_eval/cortex/providers/default.yaml
- [ ] test_agents/text_workflows/cortex/providers/default.yaml
- [ ] test_agents/no_agent/cortex/providers/default.yaml
- [ ] test_agents/agent_with_memory/cortex/providers/default.yaml
- [ ] test_agents/agent_with_temperature/cortex/providers/default.yaml
- [ ] test_agents/agent_with_eval/cortex/providers/default.yaml
- [ ] test_agents/bad_agent/cortex/providers/default.yaml
- [ ] test_agents/son_of_anton/cortex/providers/default.yaml
- [ ] test_environments/test_env_no_redis/cortex/providers/default.yaml

Test overrides with Gemma3
- [ ] test_agents/no_agent/tests/test_chat.py (6 occurrences)
- [ ] test_environments/test_env_no_redis/test_chat.py (6 occurrences)
- [ ] test_environments/test_env_local_llm/test_chat.py (9 occurrences)

0.2.0
- [ ] IDE support for injected DSL globals: ship a .pyi stub (or an optional
      no-op `import` header the runtime ignores) so agent authors get
      autocompletion and type checking for prompt(), Search, McpServer, etc.
      Same for the injected `tool` in mcp/tools/*.py (currently a ruff F821
      per-file-ignore).
- [ ] Move library ingestion out of the request pods: the PDF and chunking
      pipelines run in every replica against shared storage, so multi-pod
      deployments race on markdown rewrite and re-chunking. Single writer —
      a separate job or leader election. (Supersedes the markdown-ingestion
      note under In Consideration.)
- [ ] Multiple conversations (Need conversations endpoint?)
- [x] Local MCP tools
- [ ] Add conversation summarization feature, and memory support in cortex
- [ ] Ability to add books and create shelves on the interface.
- [ ] Wider MCP Support
- [ ] OpenAPI as tools
- [x] Local search as tool
- [ ] Extend the books endpoint, implement v2 where we see everything in the pipeline.

0.4.0
- [ ] Use a language model to get a PDF language rather than OCR_LANGUAGE environmental variable
- [ ] Make chunking hackable (?)
- [ ] (0.4.0) Add `ocr` as a provider, use this for OCR.


Anytime
- [ ] Refactor endpoint registration (api.py) to restore framework-level
      request validation: generate Pydantic models from the endpoint spec
      dicts instead of Dict[str, Any] + inspect.Signature surgery, so the
      user-facing 400s (with action suggestion + example) come from one place
      instead of hand-written checks in every handler.
- [ ] Refactor: move the env and constant assignments to one place under common
  - [ ] Refactor: move default_providers global from under api.py to somewher reasonable under common
- [ ] Refactor: under each agent, write the tests that they need to run with each environment: tests/ --> tests/default, tests/no_qdrant, tests/no_mcp
  - [ ] test_agents/agent_with_tools, also needs to run in Mistral, because of (test_agent_succeeds_when_llm_skips_tools)
  - [ ] test_agents/agent_with_eval, also needs to run in Mistral, and make sure that the eval passes, even with rate limiting.
  - [ ] On Mistral, I need to run a test to make sure that 429 rate limit exceeded errors are passed properly.
- [ ] Up arrow repeats the last message, or rolls back the conversation?
- [ ] Make sure that execute_prompt_script in agent_stem/src/common/prompt_dsl.py is removing duplicate messages, if `message_history` becomes editable.
- [ ] Create an environment to test quick fails if the environmental variables are set incorrectly, or proper error messages.
- [ ] Switch to synced-memory
- [ ] If the embedding server or mode changes, rerun the chunking, log a warning.
- [ ] Give a way to user to way for user to append to message history.



In Consideration
- [ ] Add some sort of agent_id and use as a prefix. agent:short-term-memory:<user_id>:<convo_id>
- [ ] Markdown ingestion: may have an issue, it may rewrite the same file in deployments with multiple pods.
- [ ] Update the chunking pipeline to delete files if the md does not exist, same for PDF. (Think on this: I want the markdown files to be the source of truth, but there will be a race condition if this is implemented.)




- [ ] (0.1.0) Add a test for setting a keyword differently in the agent chat if it is not set.
- [ ] (0.3.0) In workflows, if a description does not exist, fill it in from the prompt.

- [ ] (0.1.0) Log a warning every time the context window is not enough. Add to /metrics
- [ ] Introspect execute_prompt_script in agent_stem/src/common/prompt_dsl.py and make sure that docstring has all the core primitives. Then also check the docstring against the documentation and find out if anything is missing.


- [ ] In the Release Check, fail if reformatting is necessary before the tests start. If the version is not greater than the last tag, fail.

- [ ] (0.1.0) Make sure that the evaluation function is using redis-memory for storage.


- [ ] Implement streaming in the generation API. I am still seeing a message like this? tests-runner-self-hosted-llm  | .::test_openapi[POST /v1/api/generate [generated-10]] <- ../usr/local/lib/python3.12/site-packages/pytest_openapi/plugin.py PASSED [ 66%]  Request: {"model": "Lorem ipsum dolor sit amet", "prompt": ...
tests-runner-self-hosted-llm  |   Expected [200]: {"model": "gemma3:4b", "created_at": "2024-12-20T0...
tests-runner-self-hosted-llm  |   Actual [501]: {"detail": "Streaming not yet implemented"}

- [ ] Grafana integration
- [ ] Compare the chunk sizes, warn about largest chunks, suggest model and VRAM size.
- [ ] Improve chunking: detect tables, refactor the chunking library, place tests.
- [ ] (0.3.0) Add custom embedding provider. Remove EMBEDDING_HOST from env in the test environments, and remove the servers.
- [ ] (0.1.0) Change the test in no_qdrant environment to use the endpoints.
- [x] Refactor: Remove the generalize try ... except Exception blocks from multiple places.
- [ ] (0.1.0) Add open labels to the Dockerfile. Include documentation, code.
- [ ] (0.2.0) Force workflows to be streaming ndjson only.
- [ ] (0.2.0) Register workflows as MCP tools
- [ ] Give a better way to develop edit the system message dependgin on context.
- [x] (0.1.0) Something is weird with the tests. The conversations sizes seem to keep growing: (1) add some additinal info lines abouth the last message, and a median message. (2) Are the tests using the same conversation id? (3) How does conversation ids work?
      (Root cause: hard-coded conversation ids reused across runs/repeats while
      redis-test kept data between `up` invocations. All test conversation ids
      now carry a uuid4 suffix, so each run starts with empty history.)


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
