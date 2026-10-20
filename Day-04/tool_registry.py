"""
tool_registry.py  -  the "plumbing" between your tools and the AI model.

You should NEVER need to edit this file.

How it works
------------
1. In tools.py you put @tool above a normal Python function.
2. @tool reads the function's name, type hints and docstring and builds the
   JSON schema the model needs (OpenAI "function calling" format).
3. assistant.py asks this module for:
     - get_tool_schemas()  -> list sent to the model so it knows what tools exist
     - execute_tool(name, arguments_json) -> runs the tool the model picked
"""

import inspect
import json
from typing import Any, Callable, get_type_hints

# name -> {"function": <callable>, "schema": <dict>}
_REGISTRY: dict[str, dict[str, Any]] = {}

# Python type  ->  JSON-schema type
_TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _parse_docstring(doc: str) -> tuple[str, dict[str, str]]:
    """
    Split a docstring into (description, {param: description}).

    Expected (Google) style:
        Short description of the tool.

        Args:
            city: Name of the city.
            units: celsius or fahrenheit.
    """
    if not doc:
        return "", {}

    lines = inspect.cleandoc(doc).splitlines()
    description_lines, param_docs = [], {}
    in_args = False

    for line in lines:
        stripped = line.strip()
        if stripped.lower() in ("args:", "arguments:", "parameters:"):
            in_args = True
            continue
        if in_args:
            if ":" in stripped:
                name, desc = stripped.split(":", 1)
                param_docs[name.strip()] = desc.strip()
        elif stripped:
            description_lines.append(stripped)

    return " ".join(description_lines), param_docs


def _build_schema(func: Callable) -> dict:
    """Create an OpenAI tool schema from a Python function."""
    description, param_docs = _parse_docstring(func.__doc__ or "")
    hints = get_type_hints(func)
    signature = inspect.signature(func)

    properties, required = {}, []
    for name, param in signature.parameters.items():
        json_type = _TYPE_MAP.get(hints.get(name, str), "string")
        prop = {"type": json_type}
        if name in param_docs:
            prop["description"] = param_docs[name]
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            prop["default"] = param.default
        properties[name] = prop

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description or func.__name__,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def tool(func: Callable) -> Callable:
    """Decorator: register a function as a tool the AI can call."""
    _REGISTRY[func.__name__] = {"function": func, "schema": _build_schema(func)}
    return func


def get_tool_schemas() -> list[dict]:
    """All tool schemas, ready to pass as `tools=` to the model."""
    return [entry["schema"] for entry in _REGISTRY.values()]


def list_tool_names() -> list[str]:
    return list(_REGISTRY.keys())


def execute_tool(name: str, arguments_json: str) -> str:
    """
    Run the tool the model asked for and return the result as a string
    (the model only understands text). Errors are returned as text too,
    so the model can explain the problem instead of the app crashing.
    """
    if name not in _REGISTRY:
        return f"Error: unknown tool '{name}'"

    try:
        args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return f"Error: invalid arguments for '{name}': {arguments_json}"

    try:
        result = _REGISTRY[name]["function"](**args)
    except Exception as e:
        return f"Error while running '{name}': {e}"

    # default=str handles datetime, Decimal, etc.
    return result if isinstance(result, str) else json.dumps(result, default=str)
