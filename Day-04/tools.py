"""
tools.py  -  Day-04: file reader tools.

Goal: let the AI read files so it can understand, summarise and answer
questions about them.

Safety rule: the AI can only read files inside the `data/` folder next to
this file. It cannot open anything else on your computer.

To add a tool: write a function, put @tool above it, add type hints and a
docstring. assistant.py picks it up automatically.
"""

from pathlib import Path

from tool_registry import tool

# Folder the AI is allowed to read from (Day-04/data)
DATA_DIR = Path(__file__).parent / "data"

# File types we treat as plain text
ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".log",
    ".py", ".java", ".js", ".html", ".xml", ".yaml", ".yml",
}

# Don't send huge files to the AI (models have a size limit)
MAX_CHARS = 20_000


def _safe_path(filename: str) -> Path:
    """
    Turn a filename into a full path INSIDE data/.
    Blocks tricks like '../../.env' or '/etc/passwd'.
    """
    path = (DATA_DIR / filename).resolve()
    if DATA_DIR.resolve() not in path.parents:
        raise PermissionError(f"Access denied: '{filename}' is outside the data folder.")
    return path


@tool
def list_files() -> str:
    """
    List all files the assistant can read in the data folder, with their sizes.
    Use this first when the user asks what files are available or mentions a
    file without giving its exact name.
    """
    if not DATA_DIR.exists():
        return "The data folder does not exist."

    files = [p for p in sorted(DATA_DIR.rglob("*")) if p.is_file()]
    if not files:
        return "The data folder is empty."

    lines = [f"{p.relative_to(DATA_DIR)}  ({p.stat().st_size} bytes)" for p in files]
    return "\n".join(lines)


@tool
def read_text_file(filename: str) -> str:
    """
    Read a text file from the data folder and return its content, so you can
    summarise it, explain it or answer questions about it.

    Args:
        filename: Name of the file inside the data folder, e.g. notes.txt or employees.csv.
    """
    path = _safe_path(filename)

    if not path.exists():
        return f"File not found: {filename}. Call list_files to see available files."

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return f"Cannot read '{filename}': only text files are supported ({', '.join(sorted(ALLOWED_EXTENSIONS))})."

    content = path.read_text(encoding="utf-8", errors="replace")

    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + f"\n\n[... file truncated: showing first {MAX_CHARS} of {len(content)} characters]"

    return content


# Quick manual test without the AI:  python tools.py
if __name__ == "__main__":
    print("Files:\n" + list_files())
    print("\nnotes.txt:\n" + read_text_file("notes.txt"))
