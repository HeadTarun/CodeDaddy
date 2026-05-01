"""
agent/tools.py — Groq/OpenAI-compatible tool schema definitions.

Add new tools here; register the implementation in agent/call_function.py.
"""

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_files_info",
            "description": (
                "List files and subdirectories in a directory inside the sandbox. "
                "Returns name, size, and type for each entry."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Relative path to the directory. Defaults to '.' (sandbox root).",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": (
                "Read the content of a file inside the sandbox. "
                "Large files are automatically truncated."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the file.",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write (create or overwrite) a file inside the sandbox. "
                "Parent directories are created automatically."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full UTF-8 text content to write.",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_file",
            "description": (
                "Execute a Python (.py) file inside the sandbox and return stdout/stderr. "
                "Execution is time-limited."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the .py file.",
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional command-line arguments to pass to the script.",
                    },
                },
                "required": ["file_path"],
            },
        },
    },
]
