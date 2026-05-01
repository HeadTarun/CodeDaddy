import os

MAX_CHARS = 10000  # move this to config.py later


def get_file_content(working_directory, file_path):
    try:
        # Step 1: absolute working directory
        working_dir_abs = os.path.abspath(working_directory)

        # Step 2: construct safe file path
        target_path = os.path.normpath(
            os.path.join(working_dir_abs, file_path)
        )

        # Step 3: security check (prevent path traversal)
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Step 4: validate it's a file
        if not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # Step 5: read file safely with truncation
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_CHARS)

            # Check if truncated
            if f.read(1):
                content += f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return content

    except Exception as e:
        return f"Error: {str(e)}"