"""
test_file_tools.py  -  check the file tools WITHOUT the AI (no API key needed).

Run:  python test_file_tools.py
"""

from tool_registry import execute_tool
import tools  # noqa: F401

print("1) list_files")
print(execute_tool("list_files", "{}"))

print("\n2) read notes.txt")
print(execute_tool("read_text_file", '{"filename": "notes.txt"}'))

print("\n3) file that doesn't exist")
print(execute_tool("read_text_file", '{"filename": "missing.txt"}'))

print("\n4) trying to escape the data folder (should be blocked)")
print(execute_tool("read_text_file", '{"filename": "../.env"}'))
