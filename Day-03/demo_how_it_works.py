"""
demo_how_it_works.py  -  see the tool-calling flow step by step.

No API key or internet needed. Run:   python demo_how_it_works.py

It walks through what assistant.py does behind the scenes:
  STEP 1  importing tools registers every @tool function
  STEP 2  the registry turns each function into a JSON schema for the model
  STEP 3  the model replies with a "tool call" (we fake that reply here)
  STEP 4  the registry runs the matching Python function
  STEP 5  the result goes back to the model as a "tool" message
"""

import json

import tools  # noqa: F401  <- this import is what registers the tools
from tool_registry import execute_tool, get_tool_schemas, list_tool_names


def heading(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
heading("STEP 1: Tools registered by importing tools.py")
for name in list_tool_names():
    print(f"  - {name}")

# ---------------------------------------------------------------------------
heading("STEP 2: Schemas sent to the model (built from type hints + docstrings)")
print(json.dumps(get_tool_schemas(), indent=2))

# ---------------------------------------------------------------------------
heading("STEP 3: User asks a question; the model answers with TOOL CALLS")
question = "What's the time, and give me a 16 character password?"
print(f"User: {question}\n")

# This is the shape of what a real model returns when it wants tools.
# In assistant.py this comes from response.choices[0].message.tool_calls
fake_tool_calls = [
    {"id": "call_1", "name": "get_current_date_time", "arguments": "{}"},
    {"id": "call_2", "name": "generate_password", "arguments": '{"length": 16}'},
]
for call in fake_tool_calls:
    print(f"  Model wants: {call['name']}  with arguments {call['arguments']}")

# ---------------------------------------------------------------------------
heading("STEP 4: The registry runs the matching Python functions")
tool_messages = []
for call in fake_tool_calls:
    result = execute_tool(call["name"], call["arguments"])
    print(f"  {call['name']} -> {result}")
    tool_messages.append(
        {"role": "tool", "tool_call_id": call["id"], "content": result}
    )

# ---------------------------------------------------------------------------
heading("STEP 5: Results are sent back to the model as 'tool' messages")
print(json.dumps(tool_messages, indent=2))
print(
    "\nThe model now reads these results and writes the final answer, e.g.\n"
    "  Bot: It's Friday ... and here's your password: ...\n"
)

# ---------------------------------------------------------------------------
heading("BONUS: What happens with bad input (no crash, the model gets the error)")
print("  Unknown tool   ->", execute_tool("send_email", "{}"))
print("  Bad JSON       ->", execute_tool("generate_password", "{length: 16"))
print("  Wrong argument ->", execute_tool("generate_password", '{"size": 8}'))
