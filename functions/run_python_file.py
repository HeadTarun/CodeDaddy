import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    try:
        # Step 1: absolute working directory
        working_dir_abs = os.path.abspath(working_directory)

        # Step 2: construct safe target path
        target_path = os.path.normpath(
            os.path.join(working_dir_abs, file_path)
        )

        # Step 3: security check (prevent path traversal)
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Step 4: check file exists and is a file
        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        # Step 5: ensure it's a Python file
        if not target_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        # Step 6: build command
        command = ["python", target_path]

        if args:
            command.extend(args)

        # Step 7: run subprocess
        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=30
        )

        output_parts = []

        # Step 8: handle return code
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")

        # Step 9: stdout / stderr
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout.strip()}")

        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr.strip()}")

        # Step 10: no output case
        if not result.stdout and not result.stderr:
            output_parts.append("No output produced")

        return "\n".join(output_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"