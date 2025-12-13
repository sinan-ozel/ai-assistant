import logging

from fastapi import FastAPI

from startup.discover_providers import discover_providers

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

    try:
        providers_state = discover_providers()
        logger.info(f"Found {len(providers_state['available_providers'])} available providers")

        if providers_state['default_provider']:
            logger.info(f"Default provider: {providers_state['default_provider']}")
    except Exception as e:
        logger.error(f"Error discovering providers: {e}")
        # Don't fail startup, but log the error
        providers_state = {"providers": [], "available_providers": [], "default_provider": None}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/providers")
async def get_providers():
    """Get information about available providers."""
    return {
        "available": providers_state.get("available_providers", []),
        "default": providers_state.get("default_provider"),
        "total": len(providers_state.get("providers", []))
    }
