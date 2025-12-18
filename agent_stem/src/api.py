import asyncio
import functools
import inspect
import logging

from fastapi import FastAPI

from startup.providers import (discover_providers,
                               discover_context_windows)
from startup.endpoints import discover_endpoints

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai"
    }
)

# Global state for providers
providers_state = {
    "loading": True,
    "providers": [],
    "available_providers": [],
    "default_provider": None,
    "status": "initializing"
}
provider_discovery_task = None


async def run_provider_discovery():
    """Background task to discover providers and context windows."""
    global providers_state

    try:
        logger.info("Starting provider discovery in background...")

        # Run synchronous provider discovery in executor to avoid blocking
        loop = asyncio.get_event_loop()
        discovered = await loop.run_in_executor(None, discover_providers)

        # Update providers_state
        providers_state.update(discovered)

        logger.info(
            f"Found {len(providers_state['available_providers'])} available providers"
        )

        if providers_state["default_provider"]:
            logger.info(
                f"Default provider: {providers_state['default_provider']}"
            )

        # Query context windows from available providers
        if providers_state["available_providers"]:
            logger.info("Querying context windows from providers...")
            await discover_context_windows(providers_state)
            logger.info("Context window discovery complete")

        # Mark discovery as complete
        providers_state["loading"] = False
        logger.info("Provider discovery complete")

    except Exception as e:
        logger.error(f"Error during provider discovery: {e}")
        providers_state["loading"] = False
        providers_state["status"] = "error"
        providers_state["error"] = str(e)


@app.on_event("startup")
async def startup_event():
    """Run startup tasks including endpoint registration and background provider discovery."""
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

        # Determine the appropriate route handler
        if "providers_state" in params:
            # Create a wrapper that properly removes providers_state from the signature
            # This is necessary because FastAPI inspects function signatures
            async def create_wrapper(original_handler):
                async def wrapper(**kwargs):
                    return await original_handler(providers_state=providers_state, **kwargs)

                # Create new signature without providers_state parameter
                new_params = [p for p in sig.parameters.values() if p.name != "providers_state"]
                wrapper.__signature__ = inspect.Signature(parameters=new_params)
                wrapper.__name__ = original_handler.__name__
                wrapper.__doc__ = original_handler.__doc__
                return wrapper

            route_handler = await create_wrapper(handler)
        else:
            route_handler = handler

        # Register the route
        for method in spec["methods"]:
            app.add_api_route(
                spec["path"],
                route_handler,
                methods=[method],
                summary=spec.get("summary"),
                description=spec.get("description"),
                responses=spec.get("responses", {}),
            )
            logger.info(f"Registered {method} {spec['path']} from {name}")

    logger.info("API ready - provider discovery running in background")
