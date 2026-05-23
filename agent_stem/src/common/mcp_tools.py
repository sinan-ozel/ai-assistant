"""Tool discovery, validation, and schema generation for MCP servers.

Tool files are Python modules under a tools/ directory. Every public function
(not prefixed with ``_``) that is defined in the module (not imported) is
treated as an MCP tool.

Validation rules — the process crashes if any rule is violated:
- Function must have a non-empty docstring (it becomes the tool description).
- Every parameter must carry a type annotation from {str, int, float, bool,
  dict, list}.
- Every parameter must have a default value (it serves as the usage example).
- Every parameter must have a description in the Args section of the docstring.
- Parameters of type ``dict`` must not contain nested dicts in their default.

Docstring format (Google-style)::

    def search(query: str = "what is Eberron?", top_k: int = 5) -> str:
        \"\"\"Search the vector database.

        Args:
            query: The natural-language query to find relevant documents.
            top_k: Maximum number of results to return.
        \"\"\"
"""

import importlib.util
import inspect
import logging
import re
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

_SUPPORTED_TYPES: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    dict: "object",
    list: "array",
}


def _parse_args_section(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from the Args section of a Google-style
    docstring."""
    args: dict[str, str] = {}
    in_args = False
    current_param: Optional[str] = None
    current_lines: list[str] = []

    for line in docstring.splitlines():
        stripped = line.strip()

        if stripped == "Args:":
            in_args = True
            continue

        if not in_args:
            continue

        # A non-indented non-empty line that ends with ':' starts a new section.
        if stripped and not line.startswith("    ") and stripped.endswith(":"):
            in_args = False
            if current_param:
                args[current_param] = " ".join(current_lines).strip()
            break

        # Continuation of the current param description (8-space indent).
        if current_param and stripped and line.startswith("        "):
            current_lines.append(stripped)
            continue

        # New param line: 4-space indent, "param_name: description".
        match = re.match(r"^ {4}(\w+)\s*:\s*(.*)", line)
        if match:
            if current_param:
                args[current_param] = " ".join(current_lines).strip()
            current_param = match.group(1)
            current_lines = [match.group(2).strip()]

    if current_param:
        args[current_param] = " ".join(current_lines).strip()

    return args


def validate_and_build_schema(func: Callable) -> dict:
    """Validate *func* and return its MCP tool schema dict.

    Raises ``ValueError`` with an informative message on any violation.
    """
    name = func.__name__
    docstring = inspect.getdoc(func)

    if not docstring:
        msg = (
            f"Tool '{name}': a docstring is required. "
            "The docstring becomes the tool description shown to the LLM."
        )
        logger.error(msg)
        raise ValueError(msg)

    description = docstring.split("\n\n")[0].strip().replace("\n", " ")
    field_descriptions = _parse_args_section(docstring)

    hints: dict = getattr(func, "__annotations__", {}).copy()
    hints.pop("return", None)

    sig = inspect.signature(func)
    properties: dict[str, dict] = {}

    for param_name, param in sig.parameters.items():
        python_type = hints.get(param_name)

        if python_type is None:
            msg = (
                f"Tool '{name}', parameter '{param_name}': "
                "a type annotation is required."
            )
            logger.error(msg)
            raise ValueError(msg)

        if python_type not in _SUPPORTED_TYPES:
            type_name = getattr(python_type, "__name__", str(python_type))
            allowed = [t.__name__ for t in _SUPPORTED_TYPES]
            msg = (
                f"Tool '{name}', parameter '{param_name}': "
                f"unsupported type '{type_name}'. "
                f"Allowed types: {allowed}."
            )
            logger.error(msg)
            raise ValueError(msg)

        if param.default is inspect.Parameter.empty:
            msg = (
                f"Tool '{name}', parameter '{param_name}': "
                "a default value is required — it serves as the usage example "
                "shown in the tool schema."
            )
            logger.error(msg)
            raise ValueError(msg)

        if not field_descriptions.get(param_name):
            msg = (
                f"Tool '{name}', parameter '{param_name}': "
                "a description is required in the Args section of the docstring."
            )
            logger.error(msg)
            raise ValueError(msg)

        if python_type is dict and isinstance(param.default, dict):
            for k, v in param.default.items():
                if isinstance(v, dict):
                    msg = (
                        f"Tool '{name}', parameter '{param_name}': "
                        f"the default dict has a nested dict at key '{k}'. "
                        "Second-level nesting is not allowed."
                    )
                    logger.error(msg)
                    raise ValueError(msg)

        properties[param_name] = {
            "type": _SUPPORTED_TYPES[python_type],
            "description": field_descriptions[param_name],
            "default": param.default,
        }

    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
        },
    }


def discover_tools(tool_dirs: list[Path]) -> dict[str, tuple[Callable, dict]]:
    """Discover and validate all tools from the given directories.

    Scans each directory for ``*.py`` files (skipping ``_``-prefixed files).
    Every public function defined in those files (not prefixed with ``_``, not
    an import) becomes a tool.

    Returns a mapping of ``tool_name → (callable, schema)``. Raises on the
    first validation failure so misconfigured tools crash the process at
    startup rather than silently disappearing.
    """
    tools: dict[str, tuple[Callable, dict]] = {}

    for tool_dir in tool_dirs:
        if not tool_dir.exists():
            logger.debug(
                "MCP tools: directory %s does not exist — skipping.", tool_dir
            )
            continue

        for py_file in sorted(tool_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue

            logger.info("MCP tools: loading %s", py_file)
            spec = importlib.util.spec_from_file_location(
                f"mcp_tools_runtime.{py_file.stem}", py_file
            )
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as exc:
                logger.error("MCP tools: failed to import %s: %s", py_file, exc)
                raise

            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(module, attr_name)
                if (
                    not callable(attr)
                    or inspect.isclass(attr)
                    or inspect.ismodule(attr)
                ):
                    continue
                # Only include functions defined in this module, not imports.
                if getattr(attr, "__module__", None) != module.__name__:
                    continue

                schema = validate_and_build_schema(attr)

                if attr_name in tools:
                    logger.warning(
                        "MCP tools: duplicate tool name '%s' from %s — "
                        "overriding previous definition.",
                        attr_name,
                        py_file,
                    )
                tools[attr_name] = (attr, schema)
                logger.info(
                    "MCP tools: registered tool '%s' from %s.",
                    attr_name,
                    py_file,
                )

    return tools
