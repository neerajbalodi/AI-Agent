from pathlib import Path
from tools import read_text_file

file_path = Path("/Users/neerajbalodi/Desktop/AI-agent/data/notes.txt")

if not file_path.exists():
    print(f"File not found: {file_path}")
else:
    text = read_text_file(str(file_path))
    print(text)