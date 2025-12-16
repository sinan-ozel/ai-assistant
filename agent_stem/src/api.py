import logging

from fastapi import FastAPI

from startup.providers import discover_providers
from startup.endpoints import discover_endpoints

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Global state for providers
providers_state = {}


@app.on_event("startup")
async def startup_event():
    """Run startup tasks including provider discovery."""
    global providers_state

    logger.info("Starting FastAPI app...")
    logger.info("Discovering providers...")

    providers_state = discover_providers()
    logger.info(
        f"Found {len(providers_state['available_providers'])} available providers"
    )

    if providers_state["default_provider"]:
        logger.info(
            f"Default provider: {providers_state['default_provider']}"
        )

    # Discover and register endpoints
    logger.info("Discovering and registering endpoints...")
    for name, handler, spec in discover_endpoints():
        # Create a closure to capture providers_state for endpoints that need it
        if "providers" in name:

            async def route_handler():
                return await handler(providers_state)

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

