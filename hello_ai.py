from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# Create OpenAI-compatible client for Ollama
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

# Question to ask
question = "What is Kubernetes?"

# Send request
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": question}
    ]
)

# Print response
print("\nQuestion:")
print(question)

print("\nResponse:")
print(response.choices[0].message.content)