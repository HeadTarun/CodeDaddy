# 🤖 Code Agent

A local AI coding agent powered by [Groq](https://groq.com) that can read, write, and execute code inside a sandboxed workspace.

## Features

- **Filesystem tools** — list directories, read and write files
- **Code execution** — run Python scripts and capture output
- **Conversation memory** — multi-turn history saved across sessions
- **Safety sandbox** — all operations are restricted to a configurable workspace directory
- **Configurable** — all limits and model settings are environment-variable driven

## ⚠️ Security Warning

This agent can **write and execute arbitrary Python code** inside the workspace directory. Do NOT run it with untrusted inputs in production. The sandbox prevents path traversal outside the workspace, but does not isolate the process from the host OS. Use in a VM or container for untrusted workloads.

## Installation

```bash
git clone https://github.com/yourusername/code-agent
cd code-agent
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Configuration

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

All configuration options (model, limits, sandbox path) are documented in `.env.example`.

## Usage

```bash
python main.py "Create a Python script that prints the Fibonacci sequence"
python main.py "Read main.py and explain what it does"
python main.py "Fix the bug in calculator/main.py and run the tests"
```

The agent will reason step-by-step, call tools as needed, and print a final response.

### Workspace

By default the agent sandboxes all file operations inside a `workspace/` directory (create it first, or set `AGENT_WORKING_DIR` in `.env`).

```bash
mkdir workspace
```

## Project Structure

```
code-agent/
├── main.py                  # CLI entry point & agent loop
├── agent/
│   ├── config.py            # All constants & environment overrides
│   ├── tools.py             # Groq tool schema definitions
│   └── call_function.py     # Tool dispatcher
├── functions/
│   ├── get_files_info.py    # List directory contents
│   ├── get_file_content.py  # Read file
│   ├── write_file.py        # Write file
│   └── run_python_file.py   # Execute Python
├── .env.example
├── pyproject.toml
└── README.md
```

## Supported Groq Models

The default model is `llama-3.3-70b-versatile` (best tool-use accuracy). Override with `GROQ_MODEL`:

| Model | Speed | Tool-use accuracy |
|---|---|---|
| `llama-3.3-70b-versatile` | Fast | ⭐⭐⭐⭐⭐ (default) |
| `llama3-groq-70b-8192-tool-use-preview` | Faster | ⭐⭐⭐⭐ |
| `llama-3.1-8b-instant` | Fastest | ⭐⭐⭐ |

## License

MIT
