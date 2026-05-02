import asyncio
import inspect
import logging
import os
from typing import Any, Dict

from common.state import providers_state, workflows_state
from fastapi import Body, FastAPI, Request
from startup.chunking_pipeline import run_chunking_pipeline
from startup.endpoints import discover_endpoints
from startup.mcp_startup import discover_mcp_servers
from startup.pdf_pipeline import run_pdf_pipeline
from startup.providers import discover_context_windows, discover_providers
from startup.workflows import discover_workflows

# Configure logging
_log_level = getattr(
    logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO
)
logging.basicConfig(level=_log_level)
logger = logging.getLogger(__name__)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "monokai"})

provider_discovery_task = None


async def run_provider_discovery():
    """Background task to discover providers and context windows."""
    logger.info("Starting provider discovery in background...")

    # Run synchronous provider discovery in executor to avoid blocking.
    # Retry a few times if provider files exist but no providers are yet
    # available, to avoid a race where dependent LLM services become
    # ready shortly after startup.
    loop = asyncio.get_event_loop()
    max_retries = 5
    backoff_seconds = 3

    for attempt in range(1, max_retries + 1):
        discovery_result = await loop.run_in_executor(None, discover_providers)

        # Update the existing dict instead of replacing it to maintain
        # references
        providers_state.update(discovery_result)
        logger.debug("providers_state: %s", providers_state)

        available_count = len(providers_state.get("available_providers", []))
        total_providers = len(providers_state.get("providers", []))

        logger.info(
            f"Found {available_count} available providers "
            f"(attempt {attempt}/{max_retries})"
        )

        if providers_state.get("default_provider"):
            logger.info(
                f"Default provider: {providers_state['default_provider']}"
            )

        # If we have at least one available provider, proceed
        if available_count > 0:
            logger.info("Querying context windows from providers...")
            await discover_context_windows(providers_state)
            logger.info("Context window discovery complete")
            break

        # If there are no provider definitions at all, don't retry
        if total_providers == 0:
            logger.warning(
                "No provider configuration files found; skipping retries"
            )
            break

        # If this was the last attempt, stop retrying
        if attempt == max_retries:
            logger.warning(
                "Provider discovery completed with no available "
                "providers after retries"
            )
            break

        # Otherwise wait a bit and retry discovery
        logger.info(
            f"No providers available yet; retrying in {backoff_seconds}s..."
        )
        await asyncio.sleep(backoff_seconds)

    # Always mark discovery as complete so the health check can pass,
    # even if an unexpected error occurred during discovery.
    providers_state["loading"] = False
    logger.info("Provider discovery complete")


@app.on_event("startup")
async def startup_event():
    """Run startup tasks including endpoint registration and background
    provider discovery."""
    global provider_discovery_task

    logger.info("Starting FastAPI app...")

    # Start provider discovery in background
    provider_discovery_task = asyncio.create_task(run_provider_discovery())

    def _on_provider_discovery_done(task: asyncio.Task):
        logger.debug("Provider discovery task called the callback.")
        if task.cancelled():
            logger.error("Provider discovery task was cancelled.")
            os._exit(1)
        exc = task.exception()
        if exc:
            logger.error("Provider discovery failed: %s", exc, exc_info=exc)
            os._exit(1)
        logger.info("Provider discovery task completed successfully.")

    provider_discovery_task.add_done_callback(_on_provider_discovery_done)

    # Discover and validate MCP servers declared in prompt.py.
    # Run synchronously before FastAPI signals readiness so that a
    # misconfigured or unreachable server is caught immediately.
    # On failure, kill PID 1 (supervisord) to stop the restart loop.
    loop = asyncio.get_event_loop()
    try:
        mcp_result = await loop.run_in_executor(None, discover_mcp_servers)
    except Exception as exc:
        logger.error("MCP startup failed: %s", exc, exc_info=exc)
        os._exit(1)
    if mcp_result:
        logger.info("MCP startup: %d server(s) registered.", len(mcp_result))

    # Start PDF-to-Markdown pipeline in background
    asyncio.create_task(run_pdf_pipeline())

    # Start Markdown-to-chunks pipeline in background
    chunking_task = asyncio.create_task(run_chunking_pipeline())

    def _on_chunking_pipeline_done(task):
        exc = task.exception() if not task.cancelled() else None
        if exc:
            logger.error("Chunking pipeline task failed: %s", exc, exc_info=exc)
            os._exit(1)

    chunking_task.add_done_callback(_on_chunking_pipeline_done)

    # Discover and register endpoints immediately
    logger.info("Discovering and registering endpoints...")
    for name, handler, spec in discover_endpoints():
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())

        request_body_spec = spec.get("requestBody", {})
        has_request = "request" in params and request_body_spec

        if has_request:

            async def create_wrapper(
                original_handler, request_spec, handler_params
            ):
                content = request_spec.get("content", {})
                json_content = content.get("application/json", {})
                example = json_content.get("example")
                needs_headers = "headers" in handler_params

                async def wrapper(
                    request: Dict[str, Any] = Body(
                        ...,
                        openapi_examples=(
                            {"example": {"value": example}} if example else None
                        ),
                    ),
                    fastapi_request: Request = None,
                    **path_params,
                ):
                    kwargs = {"request": request}
                    if needs_headers:
                        kwargs["headers"] = (
                            dict(fastapi_request.headers)
                            if fastapi_request
                            else {}
                        )
                    kwargs.update(path_params)
                    return await original_handler(**kwargs)

                excluded = {"request", "headers"}
                new_params = [
                    p for p in sig.parameters.values() if p.name not in excluded
                ]
                body_param = inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Dict[str, Any],
                )
                fastapi_request_param = inspect.Parameter(
                    "fastapi_request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                )
                new_params = [body_param, fastapi_request_param] + new_params

                wrapper.__signature__ = inspect.Signature(parameters=new_params)
                wrapper.__name__ = original_handler.__name__
                wrapper.__doc__ = original_handler.__doc__
                return wrapper

            route_handler = await create_wrapper(
                handler, request_body_spec, params
            )
        else:
            route_handler = handler

        # Register the route
        # Enforce that every endpoint documents at least one success response.
        responses = spec.get("responses") or {}
        if not any(c in responses for c in (200, 201, 202)):
            raise RuntimeError(
                f"Endpoint '{name}' ({' '.join(spec['methods'])} {spec['path']}) "
                "must document at least one of 200, 201, or 202 in its responses spec."
            )

        for method in spec["methods"]:
            openapi_extra = {}
            if request_body_spec:
                openapi_extra["requestBody"] = request_body_spec

            # Determine status code from spec; default to 200.
            # If the spec defines 2xx responses but not 200, use the lowest one
            # so FastAPI doesn't auto-generate a blocking 200 primary response.
            status_code = 200
            if spec.get("responses") and 200 not in spec["responses"]:
                success_codes = sorted(
                    c
                    for c in spec["responses"]
                    if isinstance(c, int) and 200 <= c < 300
                )
                if success_codes:
                    status_code = success_codes[0]

            tag = "private" if spec["path"].startswith("/private") else "public"
            app.add_api_route(
                spec["path"],
                route_handler,
                methods=[method],
                summary=spec.get("summary"),
                description=spec.get("description"),
                responses=spec.get("responses", {}),
                status_code=status_code,
                openapi_extra=openapi_extra,
                tags=[tag],
            )
            logger.info(f"Registered {method} {spec['path']} from {name}")

    # Discover and register workflow endpoints
    logger.info("Discovering and registering workflow endpoints...")
    async for (
        name,
        handler,
        spec,
        workflow_data,
        workflow_file,
    ) in discover_workflows():
        # Store workflow in global state
        workflow_path = workflow_data.get("path")
        if workflow_path:
            workflows_state["workflows"][workflow_path] = {
                "name": name,
                "data": workflow_data,
                "file": workflow_file,
            }
            logger.info(f"Stored workflow {name} with path {workflow_path}")

        # Extract request schema from spec
        request_body_spec = spec.get("requestBody", {})
        content = request_body_spec.get("content", {})
        json_content = content.get("application/json", {})
        example = json_content.get("example")

        async def create_workflow_wrapper(original_handler):
            async def wrapper(
                request: Dict[str, Any] = Body(
                    ...,
                    openapi_examples=(
                        {"example": {"value": example}} if example else None
                    ),
                )
            ):
                return await original_handler(request=request)

            wrapper.__signature__ = inspect.Signature(
                parameters=[
                    inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Dict[str, Any],
                    )
                ]
            )
            wrapper.__name__ = original_handler.__name__
            wrapper.__doc__ = original_handler.__doc__
            return wrapper

        route_handler = await create_workflow_wrapper(handler)

        # Register the route
        for method in spec["methods"]:
            openapi_extra = {}
            if request_body_spec:
                openapi_extra["requestBody"] = request_body_spec

            app.add_api_route(
                spec["path"],
                route_handler,
                methods=[method],
                summary=spec.get("summary"),
                description=spec.get("description"),
                responses=spec.get("responses", {}),
                openapi_extra=openapi_extra,
                tags=["workflows"],
            )
            logger.info(
                f"Registered {method} {spec['path']} from workflow {name}"
            )

    logger.info("API ready - provider discovery running in background")
