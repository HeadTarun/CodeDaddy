import os


def write_file(working_directory, file_path, content):
    try:
        # Step 1: absolute working directory
        working_dir_abs = os.path.abspath(working_directory)

        # Step 2: construct safe target path
        target_path = os.path.normpath(
            os.path.join(working_dir_abs, file_path)
        )

        # Step 3: security check (prevent path traversal)
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # Step 4: prevent writing to a directory
        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        # Step 5: ensure parent directories exist
        parent_dir = os.path.dirname(target_path)
        os.makedirs(parent_dir, exist_ok=True)

        # Step 6: write content
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {str(e)}"