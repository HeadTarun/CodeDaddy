import os
import json
from dotenv import load_dotenv
from groq import Groq
import sys

HISTORY_FILE = "chat_history.json"
MAX_MESSAGES = 20

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def trim_history(history):
    return history[-MAX_MESSAGES:]

def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    client = Groq(api_key=api_key)

    # ✅ KEEPING YOUR CLI STYLE
    if len(sys.argv) < 2:
        print("Please provide a prompt as a command-line argument.")
        sys.exit(1)

    prompt = sys.argv[1]

    # 🔥 Load previous conversation
    history = load_history()

    # add user message
    history.append({
        "role": "user",
        "content": prompt
    })

    # trim history
    history = trim_history(history)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=history
    )

    reply = response.choices[0].message.content

    print(reply)

    # add assistant reply
    history.append({
        "role": "assistant",
        "content": reply
    })

    # save back
    save_history(history)


if __name__ == "__main__":
    main()