from openai import OpenAI
from dotenv import load_dotenv
import os
from tools import (
    get_current_date_time,
    generate_password
)

# Load configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# Create AI Client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

print("=" * 40)
print("    My AI Assistant")
print("=" * 40)

messages = []

while True:
    question = input("You: ").strip()

    if question.lower() == "quit":
        print("Exiting chat. Goodbye!")
        break

    # Check if user is asking about time
    if "time" in question.lower():
        current_time = get_current_date_time()
        print(f"\nBot: The current date and time is {current_time}\n")
        continue

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

        answer = response.choices[0].message.content

        print(f"\nBot: {answer}\n")

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:
        print(f"\nError: {e}\n")