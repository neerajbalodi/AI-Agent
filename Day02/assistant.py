from openai import OpenAI
from dotenv import load_dotenv
import os

# load configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# Create AI Client
client=OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

print("=" *40)
print("    My AI Assistant")
print("=" *40)

messages = [
    {
        "role": "assistant",
        "content": "Act as expert Doctor"
    }
]

while True:
    question = input("You: ").strip()

    if question.lower() == "quit":
        print("Exiting chat. Goodbye!")
        break

    messages.append(
        {
            "role":"user",
            "content":question
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
                "role":"assistant",
                "content":answer
            }
        )

        # print(f"\nConversation History ================")

        # for message in messages:
        #     print(f"{message['role'].title()} : {message['content']}")

    except Exception as e:
        print(f"\nError: {e}\n")