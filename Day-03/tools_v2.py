"""
tools_v2.py  -  the ONLY file you edit to give the assistant new abilities.

To add a tool:
  1. Write a normal Python function.
  2. Put @tool above it.
  3. Add type hints on the parameters (str, int, float, bool).
  4. Write a docstring: first line = what the tool does (the model reads this
     to decide WHEN to use it), and an "Args:" section describing each parameter.

That's it - assistant_v2.py picks it up automatically.
"""

from datetime import datetime
import secrets
import string

from tool_registry import tool


@tool
def get_current_date_time() -> str:
    """Get the current local date and time. Use this whenever the user asks about the time, date or day."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M:%S %p")


@tool
def generate_password(length: int = 12) -> str:
    """
    Generate a strong random password with letters, digits and symbols.

    Args:
        length: Number of characters in the password (default 12).
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


# ---------------------------------------------------------------------------
# Example of adding a new tool later - just uncomment, nothing else changes:
#
# @tool
# def add_numbers(a: float, b: float) -> float:
#     """
#     Add two numbers together.
#
#     Args:
#         a: First number.
#         b: Second number.
#     """
#     return a + b
# ---------------------------------------------------------------------------


# Quick manual test:  python tools_v2.py
# (inside this block so it does NOT run when assistant_v2.py imports the file)
if __name__ == "__main__":
    print(get_current_date_time())
    print(generate_password())
