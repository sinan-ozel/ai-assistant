.PHONY: test clean build help

help:
	@echo "Available targets:"
	@echo "  make test   - Run all tests in isolated Docker environment"
	@echo "  make build  - Build the agent_stem Docker image"
	@echo "  make clean  - Clean up test containers and networks"
	@echo "  make help   - Show this help message"

test:
	docker compose \
		-f test_environments/test_env_nothing/docker-compose.yaml \
		--project-directory test_environments/test_env_nothing \
		up \
		--build \
		--abort-on-container-exit \
		--exit-code-from tests
	docker compose \
		-f test_environments/test_env_no_llm/docker-compose.yaml \
		--project-directory test_environments/test_env_no_llm \
		up \
		--build \
		--abort-on-container-exit \
		--exit-code-from tests
	docker compose \
		-f test_environments/test_env_self_hosted_llm/docker-compose.yaml \
		--project-directory test_environments/test_env_self_hosted_llm \
		up \
		--build \
		--abort-on-container-exit \
		--exit-code-from tests
	docker compose \
		-f test_environments/test_env_mistral/docker-compose.yaml \
		--project-directory test_environments/test_env_mistral \
		up \
		--build \
		--abort-on-container-exit \
		--exit-code-from tests

build:
	docker build -t agent-stem:latest agent_stem/

clean:
	docker compose -f test_environments/test_env_no_llm/docker-compose.yaml --project-directory test_environments/test_env_no_llm down -v
	rm -rf test_environments/test_env_no_llm/test-results/*
