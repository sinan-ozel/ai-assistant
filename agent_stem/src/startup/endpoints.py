"""Endpoint discovery and registration module."""

import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINTS_DIR = Path("/app/default/endpoints")


def load_endpoint_module(endpoint_file: Path) -> Dict[str, Any]:
    """Load an endpoint module from a Python file.

    Args:
        endpoint_file: Path to the endpoint Python file

    Returns:
        Dictionary with 'handler' and 'spec' keys
    """
    module_name = f"endpoints.{endpoint_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, endpoint_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load spec from {endpoint_file}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "handler"):
        raise RuntimeError(
            f"Endpoint {endpoint_file} missing 'handler' function"
        )
    if not hasattr(module, "spec"):
        raise RuntimeError(
            f"Endpoint {endpoint_file} missing 'spec' dictionary"
        )

    return {"handler": module.handler, "spec": module.spec}


def discover_endpoints(endpoints_dir: Path = DEFAULT_ENDPOINTS_DIR):
    """Discover and load all endpoint modules recursively.

    Args:
        endpoints_dir: Directory containing endpoint Python files

    Yields:
        Tuples of (endpoint_name, handler, spec)
    """
    if not endpoints_dir.exists():
        logger.warning(f"Endpoints directory not found: {endpoints_dir}")
        return

    for endpoint_file in sorted(endpoints_dir.rglob("*.py")):
        if endpoint_file.name.startswith("_"):
            continue

        try:
            logger.info(
                f"Loading endpoint: {endpoint_file.relative_to(endpoints_dir)}"
            )
            endpoint_module = load_endpoint_module(endpoint_file)
            yield endpoint_file.stem, endpoint_module[
                "handler"
            ], endpoint_module["spec"]
        except Exception as e:
            logger.error(f"Failed to load endpoint {endpoint_file.name}: {e}")
            raise
