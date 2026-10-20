"""
Day-05: Create 2 embeddings and compare them.

Before running:
  1. Ollama is running
  2. ollama pull nomic-embed-text

Run:  python3 create_embeddings.py
"""

import math

from openai import OpenAI

# Ollama runs on your laptop and speaks the same API as OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


# Step 1: Two sentences with the SAME meaning but DIFFERENT words
sentence1 = "I am hungry"
sentence2 = "Let's get something to eat"


# Step 2: Ask the model to turn each sentence into numbers (an embedding)
response = client.embeddings.create(
    model="nomic-embed-text",
    input=[sentence1, sentence2],
)

embedding1 = response.data[0].embedding
embedding2 = response.data[1].embedding


# Step 3: Look at what an embedding is
print("Sentence 1:", sentence1)
print("Numbers in embedding:", len(embedding1))
print("First 5 numbers:", embedding1[:5])
print()
print("Sentence 2:", sentence2)
print("Numbers in embedding:", len(embedding2))
print("First 5 numbers:", embedding2[:5])
print()


# Step 4: Compare them (cosine similarity: higher = more similar meaning)
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    size_a = math.sqrt(sum(x * x for x in a))
    size_b = math.sqrt(sum(y * y for y in b))
    return dot / (size_a * size_b)


score = cosine_similarity(embedding1, embedding2)
print(f"Similarity: {score:.3f}")
