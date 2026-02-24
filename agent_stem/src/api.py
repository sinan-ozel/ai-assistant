import asyncio
import inspect
import logging
from typing import Any, Dict

from fastapi import Body, FastAPI
from startup.endpoints import discover_endpoints
from startup.providers import discover_context_windows, discover_providers
from startup.workflows import discover_workflows

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "monokai"})

# Global state for providers
providers_state = {
    "loading": True,
    "providers": [],
    "available_providers": [],
    "default_provider": None,
    "status": "initializing",
}
provider_discovery_task = None


async def run_provider_discovery():
    """Background task to discover providers and context windows."""
    global providers_state
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

    # Mark discovery as complete
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

    # Discover and register endpoints immediately
    logger.info("Discovering and registering endpoints...")
    for name, handler, spec in discover_endpoints():
        # Inspect handler signature to determine how to wrap it
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())

        # Check if endpoint has a request body schema
        request_body_spec = spec.get("requestBody", {})
        has_request = "request" in params and request_body_spec

        # Determine the appropriate route handler
        if "providers_state" in params or has_request:
            # Create a wrapper that properly removes providers_state
            # from the signature and adds proper Body parameter for
            # request body validation
            async def create_wrapper(original_handler, request_spec):
                if has_request:
                    # Extract schema from requestBody
                    content = request_spec.get("content", {})
                    json_content = content.get("application/json", {})
                    example = json_content.get("example")

                    # Create Body parameter with schema
                    body_param = inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=Body(
                            ...,
                            openapi_examples=(
                                {"example": {"value": example}}
                                if example
                                else None
                            ),
                        ),
                        annotation=Dict[str, Any],
                    )

                    async def wrapper(
                        request: Dict[str, Any] = Body(
                            ...,
                            openapi_examples=(
                                {"example": {"value": example}}
                                if example
                                else None
                            ),
                        )
                    ):
                        if "providers_state" in params:
                            return await original_handler(
                                request=request, providers_state=providers_state
                            )
                        else:
                            return await original_handler(request=request)

                else:

                    async def wrapper(**kwargs):
                        return await original_handler(
                            providers_state=providers_state, **kwargs
                        )

                # Create new signature without providers_state parameter
                new_params = [
                    p
                    for p in sig.parameters.values()
                    if p.name not in ["providers_state", "request"]
                ]
                if has_request:
                    # Add request parameter with Body annotation
                    body_param = inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Dict[str, Any],
                    )
                    new_params = [body_param] + new_params

                wrapper.__signature__ = inspect.Signature(parameters=new_params)
                wrapper.__name__ = original_handler.__name__
                wrapper.__doc__ = original_handler.__doc__
                return wrapper

            route_handler = await create_wrapper(handler, request_body_spec)
        else:
            route_handler = handler

        # Register the route
        for method in spec["methods"]:
            # Build openapi_extra with requestBody schema
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
            )
            logger.info(f"Registered {method} {spec['path']} from {name}")

    # Discover and register workflow endpoints
    logger.info("Discovering and registering workflow endpoints...")
    async for name, handler, spec in discover_workflows():
        # Workflow handlers always need providers_state and request body
        sig = inspect.signature(handler)

        # Extract request schema from spec
        request_body_spec = spec.get("requestBody", {})
        content = request_body_spec.get("content", {})
        json_content = content.get("application/json", {})
        example = json_content.get("example")

        # Create wrapper that injects providers_state
        async def create_workflow_wrapper(original_handler):
            async def wrapper(
                request: Dict[str, Any] = Body(
                    ...,
                    openapi_examples=(
                        {"example": {"value": example}} if example else None
                    ),
                )
            ):
                return await original_handler(
                    request=request, providers_state=providers_state
                )

            # Create signature without providers_state
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
            )
            logger.info(
                f"Registered {method} {spec['path']} from workflow {name}"
            )

    logger.info("API ready - provider discovery running in background")
