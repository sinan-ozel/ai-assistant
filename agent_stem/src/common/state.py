"""Shared mutable state for providers and workflows.

Both api.py and endpoint modules import from here to avoid circular imports.
api.py updates these dicts in-place; endpoints read them directly.
"""

providers_state: dict = {
    "loading": True,
    "providers": [],
    "available_providers": [],
    "default_provider": None,
    "status": "initializing",
}

workflows_state: dict = {
    "workflows": {},
}
