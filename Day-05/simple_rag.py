"""
Day-05: Simple RAG (Retrieval-Augmented Generation)

Ask questions about data/handbook.txt (about 100 pages).
Instead of sending the whole handbook to the AI, we:
  1. FIND the 3 paragraphs closest in meaning to the question (embeddings)
  2. ANSWER by sending only those 3 paragraphs + the question to the chat model

Before running:
  - Ollama is running and `ollama pull nomic-embed-text` is done
  - .env has BASE_URL, API_KEY and MODEL for your chat model (same as Day-04)

Run:  python3 simple_rag.py
"""

import json
import math
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Two clients: one for embeddings (Ollama on this laptop), one for answers (chat model)
embed_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
chat_client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
CHAT_MODEL = os.getenv("MODEL")

HANDBOOK_FILE = "data/handbook.txt"
EMBEDDINGS_FILE = "data/embeddings.json"   # saved after the first run
TOP_K = 3                                  # how many paragraphs to send to the AI


def embed(texts):
    """Turn a list of texts into a list of embeddings (768 numbers each)."""
    response = embed_client.embeddings.create(model="nomic-embed-text", input=texts)
    return [item.embedding for item in response.data]


def cosine_similarity(a, b):
    """Same function as create_embeddings.py: higher = more similar meaning."""
    dot = sum(x * y for x, y in zip(a, b))
    size_a = math.sqrt(sum(x * x for x in a))
    size_b = math.sqrt(sum(y * y for y in b))
    return dot / (size_a * size_b)


# ---------------------------------------------------------------------------
# PHASE 1: PREPARE (once)
# ---------------------------------------------------------------------------

# Step 1: Read the handbook
with open(HANDBOOK_FILE, encoding="utf-8") as f:
    text = f.read()

# Step 2: Cut it into chunks - one paragraph (separated by a blank line) = one chunk.
# Skip tiny chunks like chapter titles ("CHAPTER 4: LEAVE POLICY").
chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) >= 60]
print(f"Handbook split into {len(chunks)} chunks")

# Step 3: Embed every chunk - or load the numbers saved from a previous run
if os.path.exists(EMBEDDINGS_FILE):
    with open(EMBEDDINGS_FILE) as f:
        saved = json.load(f)
else:
    saved = None

if saved and saved["chunks"] == chunks:
    chunk_embeddings = saved["embeddings"]
    print("Loaded saved embeddings (no need to recalculate)")
else:
    print("Creating embeddings for the first time - this takes a while...")
    chunk_embeddings = []
    batch_size = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        chunk_embeddings += embed(["search_document: " + c for c in batch])
        print(f"  embedded {min(i + batch_size, len(chunks))} / {len(chunks)}")
    with open(EMBEDDINGS_FILE, "w") as f:
        json.dump({"chunks": chunks, "embeddings": chunk_embeddings}, f)
    print(f"Saved embeddings to {EMBEDDINGS_FILE}")


# ---------------------------------------------------------------------------
# PHASE 2: ANSWER (for every question)
# ---------------------------------------------------------------------------

print("\nAsk a question about the Nimbus Softech handbook. Type 'quit' to exit.\n")

while True:
    question = input("You: ").strip()
    if not question:
        continue
    if question.lower() == "quit":
        break

    # Step 4: Embed the question
    question_embedding = embed(["search_query: " + question])[0]

    # Step 5: Compare with every chunk and keep the TOP_K closest
    scores = [cosine_similarity(question_embedding, e) for e in chunk_embeddings]
    best = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:TOP_K]

    # Step 8 (shown first): print what we found, so students can see the retrieval
    print("\nFound:")
    for i in best:
        title = chunks[i].split("\n")[0]
        print(f"  {scores[i]:.3f}  {title}")

    # Step 6: Build the prompt from ONLY the found chunks
    context = "\n\n".join(chunks[i] for i in best)
    prompt = (
        "Answer the question using ONLY the information below. "
        "If the answer is not in the information, say \"I don't know based on the handbook.\" "
        "Mention the section number you used.\n\n"
        f"Information:\n{context}\n\n"
        f"Question: {question}"
    )

    # Step 7: Ask the chat model
    try:
        response = chat_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        print(f"\nBot: {response.choices[0].message.content}\n")
    except Exception as e:
        print(f"\nError: {e}\n")
