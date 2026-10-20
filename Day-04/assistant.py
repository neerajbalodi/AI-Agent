"""
assistant.py  -  Day-04: AI assistant that can read files.

Same tool-calling loop as Day-03. The AI decides when it needs to read a
file, our code reads it, and the file content is sent back to the AI so it
can understand it and answer.

You don't edit this file to add tools - add them in tools.py.

Try asking:
  - What files do you have?
  - Summarise notes.txt
  - Who earns the most in employees.csv?
  - Explain what calculator.py does
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

import tools  # noqa: F401  (importing registers every @tool function)
from tool_registry import execute_tool, get_tool_schemas, list_tool_names

# Load configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# Safety limit: max tool-call rounds for one user question
MAX_TOOL_ROUNDS = 5

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

TOOLS = get_tool_schemas()

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant that can read the user's files. "
            "When the user asks about a file, use read_text_file to read it "
            "before answering - never guess what a file contains. If you "
            "don't know the exact filename, call list_files first. Base your "
            "answers on the file content."
        ),
    }
]


def chat(question: str) -> str:
    """Send a question, let the model use tools as needed, return the final answer."""
    messages.append({"role": "user", "content": question})

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        # No tool needed -> final answer
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content

        # Record the model's tool request
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

        # Run each tool and send the result (e.g. the file content) back
        for call in msg.tool_calls:
            print(f"  [tool] {call.function.name}({call.function.arguments})")
            result = execute_tool(call.function.name, call.function.arguments)
            print(f"  [tool] returned {len(result)} characters")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    return "Sorry, I couldn't finish that (too many tool calls)."


def main():
    print("=" * 40)
    print("    My AI Assistant - File Reader")
    print("=" * 40)
    print(f"Tools loaded: {', '.join(list_tool_names())}")
    print("Put files in the data/ folder. Type 'quit' to exit.\n")

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
