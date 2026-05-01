import os
import json
import sys
from dotenv import load_dotenv
from groq import Groq

from call_function import call_function

# ==============================
# CONFIG
# ==============================
HISTORY_FILE = "chat_history.json"
MAX_MESSAGES = 30
MAX_ITERATIONS = 8
MODEL = "openai/gpt-oss-120b"

# ==============================
# SYSTEM PROMPT
# ==============================
system_prompt = """
You are an AI coding agent.

You can:
- List files and directories
- Read file contents
- Write or overwrite files
- Execute Python files

Rules:
- Always use tools when needed
- Use relative paths only
- Never mention working_directory
- Solve tasks step-by-step using tools

When no tool is needed, respond normally.
"""

# ==============================
# TOOL SCHEMA (Groq)
# ==============================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_files_info",
            "description": "List files in a directory",
            "parameters": {"type": "object", "properties": {"directory": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": "Read file content",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_file",
            "description": "Execute Python file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "args": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["file_path"]
            }
        }
    }
]

# ==============================
# HISTORY
# ==============================
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def trim_history(history):
    system = history[0] if history else None
    trimmed = history[-MAX_MESSAGES:]
    return [system] + trimmed if system else trimmed

# ==============================
# MAIN AGENT LOOP
# ==============================
def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("Error: GROQ_API_KEY not found")
        sys.exit(1)

    client = Groq(api_key=api_key)

    if len(sys.argv) < 2:
        print("Provide prompt")
        sys.exit(1)

    user_input = sys.argv[1]

    history = load_history()

    # Inject system prompt once
    if not any(m["role"] == "system" for m in history):
        history.insert(0, {"role": "system", "content": system_prompt})

    history.append({"role": "user", "content": user_input})
    history = trim_history(history)

    iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1

        response = client.chat.completions.create(
            model=MODEL,
            messages=history,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )

        message = response.choices[0].message

        # ==============================
        # ALWAYS append assistant message
        # ==============================
        history.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": message.tool_calls
        })

        # ==============================
        # TOOL CALL CASE
        # ==============================
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result = call_function(tool_call)

                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            continue

        # ==============================
        # FINAL RESPONSE
        # ==============================
        if message.content:
            print("\nFinal Response:\n")
            print(message.content)
            break

    else:
        print("Error: Max iterations reached (agent stuck)")
        sys.exit(1)

    save_history(history)


if __name__ == "__main__":
    main()