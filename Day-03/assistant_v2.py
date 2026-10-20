"""
assistant_v2.py  -  chat loop with automatic tool calling.

You should not need to edit this file when adding tools.
Add tools in tools_v2.py instead.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

import tools_v2  # noqa: F401  (importing registers every @tool function)
from tool_registry import execute_tool, get_tool_schemas, list_tool_names

# Load configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# Safety limit: max tool-call rounds for a single user question
MAX_TOOL_ROUNDS = 5

# Create AI client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

TOOLS = get_tool_schemas()

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. When a question needs live or "
            "computed information, use the available tools instead of guessing."
        ),
    }
]


def ask_model():
    """One call to the model, offering it our tools."""
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )


def chat(question: str) -> str:
    """Send a question, let the model use tools as needed, return final answer."""
    messages.append({"role": "user", "content": question})

    for _ in range(MAX_TOOL_ROUNDS):
        response = ask_model()
        msg = response.choices[0].message

        # No tool needed -> this is the final answer
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content

        # The model wants tools: record its request...
        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in msg.tool_calls
                ],
            }
        )

        # ...run each tool and send the results back
        for call in msg.tool_calls:
            print(f"  [tool] {call.function.name}({call.function.arguments})")
            result = execute_tool(call.function.name, call.function.arguments)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )
        # loop again so the model can use the results

    return "Sorry, I couldn't finish that (too many tool calls)."


def main():
    print("=" * 40)
    print("    My AI Assistant")
    print("=" * 40)
    print(f"Tools loaded: {', '.join(list_tool_names())}")
    print("Type 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            print("Exiting chat. Goodbye!")
            break

        try:
            answer = chat(question)
            print(f"\nBot: {answer}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
