import os

def get_files_info(working_directory, directory="."):
    try:
        # Step 1: Absolute path of working directory
        working_dir_abs = os.path.abspath(working_directory)

        # Step 2: Build target directory path safely
        target_dir = os.path.normpath(
            os.path.join(working_dir_abs, directory)
        )

        # Step 3: Security check (prevent path traversal)
        if os.path.commonpath([working_dir_abs, target_dir]) != working_dir_abs:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Step 4: Check if it's a directory
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        # Step 5: List contents
        items = os.listdir(target_dir)

        result_lines = []

        for item in items:
            item_path = os.path.join(target_dir, item)

            try:
                file_size = os.path.getsize(item_path)
                is_dir = os.path.isdir(item_path)

                result_lines.append(
                    f"- {item}: file_size={file_size} bytes, is_dir={is_dir}"
                )
            except Exception as e:
                result_lines.append(
                    f"- {item}: Error accessing item ({str(e)})"
                )

        return "\n".join(result_lines)

    except Exception as e:
        return f"Error: {str(e)}"