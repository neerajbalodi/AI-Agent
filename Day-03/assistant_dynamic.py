"""
assistant_dynamic.py  -  tools are loaded ON DEMAND, not at startup.

Difference from assistant.py
----------------------------
assistant.py      : sends EVERY tool's description to the model on every call.
assistant_dynamic : the model starts with ONE tool, `search_tools`.
                    When it needs a capability, it searches; matching tools
                    are then "loaded" (added to the list sent to the model)
                    and stay loaded for the rest of the chat.

Why: with 2 tools it makes no difference. With 50+ tools, sending all of
them every time wastes tokens and confuses the model. Real agent systems
use this "tool search" pattern.

tools.py and tool_registry.py are used exactly as they are.
"""

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

import tools  # noqa: F401  (registers @tool functions - nothing RUNS yet)
from tool_registry import execute_tool, get_tool_schemas

load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
MODEL = os.getenv("MODEL")
MAX_TOOL_ROUNDS = 5

# Catalog of every tool we COULD load: name -> schema
CATALOG = {s["function"]["name"]: s for s in get_tool_schemas()}

# Tools currently loaded (sent to the model). Starts EMPTY.
loaded_tools: set[str] = set()


# ---------------------------------------------------------------------------
# The one tool the model always has: search_tools
# ---------------------------------------------------------------------------
SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_tools",
        "description": (
            "Search for tools that can help with the user's request "
            "(e.g. 'current time', 'password'). Matching tools become "
            "available to call right after this."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords describing what you need to do.",
                }
            },
            "required": ["query"],
        },
    },
}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower().replace("_", " ")))


def search_tools(query: str) -> str:
    """Find tools whose name/description share words with the query and load them."""
    query_words = _words(query)
    found = []
    for name, schema in CATALOG.items():
        tool_words = _words(name + " " + schema["function"]["description"])
        if query_words & tool_words:
            found.append(name)
            if name not in loaded_tools:
                loaded_tools.add(name)
                print(f"  [loaded] {name}")

    if not found:
        return json.dumps(
            {"loaded": [], "hint": "No match. Try other keywords.",
             "available_names": list(CATALOG)}
        )
    return json.dumps(
        {"loaded": [{"name": n, "description": CATALOG[n]["function"]["description"]}
                    for n in found]}
    )


def current_tool_list() -> list[dict]:
    """What the model sees on THIS call: search_tools + whatever is loaded."""
    return [SEARCH_TOOL_SCHEMA] + [CATALOG[n] for n in sorted(loaded_tools)]


# ---------------------------------------------------------------------------
# Chat loop (same as assistant.py, but the tool list is rebuilt every call)
# ---------------------------------------------------------------------------
messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. You start with only the "
            "`search_tools` tool. If a request needs live data or an action "
            "you can't do yourself, first call search_tools with short "
            "keywords, then call the tool it loads. Don't guess live data."
        ),
    }
]


def chat(question: str) -> str:
    messages.append({"role": "user", "content": question})

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=current_tool_list(),   # <- changes as tools get loaded
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {"id": c.id, "type": "function",
                     "function": {"name": c.function.name,
                                  "arguments": c.function.arguments}}
                    for c in msg.tool_calls
                ],
            }
        )

        for call in msg.tool_calls:
            name, args = call.function.name, call.function.arguments
            print(f"  [tool] {name}({args})")

            if name == "search_tools":
                result = search_tools(**json.loads(args or "{}"))
            elif name in loaded_tools:
                result = execute_tool(name, args)
            else:
                result = f"Error: '{name}' is not loaded. Call search_tools first."

            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    return "Sorry, I couldn't finish that (too many tool calls)."


def main():
    print("=" * 40)
    print("    My AI Assistant (dynamic tools)")
    print("=" * 40)
    print(f"Tools available: {len(CATALOG)}  |  loaded: 0 (loaded on demand)")
    print("Type 'quit' to exit, 'tools' to see what's loaded.\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            print("Exiting chat. Goodbye!")
            break
        if question.lower() == "tools":
            print(f"  Loaded: {sorted(loaded_tools) or 'none'}\n")
            continue
        try:
            print(f"\nBot: {chat(question)}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
