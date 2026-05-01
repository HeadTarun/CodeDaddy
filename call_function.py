import json

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

WORKING_DIRECTORY = "calculator"

# 🔥 Central tool registry
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(tool_call):
    """
    Executes a tool call from Groq (OpenAI-style tool_calls)
    """

    # Extract function name safely
    function_name = getattr(tool_call.function, "name", "") or ""

    # Parse arguments safely
    try:
        raw_args = getattr(tool_call.function, "arguments", "{}")
        args = json.loads(raw_args) if raw_args else {}
        if not isinstance(args, dict):
            args = {}
    except Exception:
        args = {}

    # Basic log (always useful)
    print(f"[TOOL CALL] {function_name} | args={args}")

    # Validate function
    if function_name not in FUNCTION_MAP:
        return f"Error: Unknown function: {function_name}"

    # Inject working directory (secure override)
    args["working_directory"] = WORKING_DIRECTORY

    # Execute safely
    try:
        result = FUNCTION_MAP[function_name](**args)
    except Exception as e:
        result = f"Error executing {function_name}: {str(e)}"

    # Optional: trim huge outputs (LLM safety)
    MAX_OUTPUT = 5000
    if isinstance(result, str) and len(result) > MAX_OUTPUT:
        result = result[:MAX_OUTPUT] + "\n[...output truncated]"

    return result