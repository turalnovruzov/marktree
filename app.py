import os
import streamlit as st
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def load_gitignore_patterns(gitignore_path):
    """
    Read .gitignore file and convert it into a PathSpec object.
    If no .gitignore found, returns None.
    """
    if not os.path.isfile(gitignore_path):
        return None

    with open(gitignore_path, "r") as f:
        gitignore_contents = f.read().splitlines()

    # Create a PathSpec from the read patterns
    spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_contents)
    return spec


def gather_files_and_folders(root_path, spec=None, project_root=None):
    """
    Recursively gather all files and folders from root_path,
    excluding those matched by the .gitignore spec if present,
    and explicitly excluding the .git directory.
    Returns a nested list/dict structure for the tree.

    Parameters:
    - root_path: Current directory being traversed.
    - spec: PathSpec object containing .gitignore patterns.
    - project_root: The root directory of the project (constant throughout recursion).
    """
    if project_root is None:
        project_root = root_path  # Initialize project_root on the first call

    tree = []

    try:
        entries = sorted(os.listdir(root_path))
    except PermissionError:
        # Skip directories for which the user does not have permission
        return tree

    for entry in entries:
        # **Exclude the `.git` directory explicitly**
        if entry == ".git":
            continue

        full_path = os.path.join(root_path, entry)

        # Calculate the relative path to the project root
        rel_path = os.path.relpath(full_path, start=project_root)

        # Normalize path separators to '/' as PathSpec expects Unix-style paths
        rel_path = rel_path.replace(os.path.sep, "/")

        # If we have a spec and this path is ignored, skip it
        if spec and spec.match_file(rel_path):
            continue

        if os.path.isdir(full_path):
            # Recursively gather subfolders
            subtree = gather_files_and_folders(full_path, spec, project_root)
            if subtree:  # If folder not empty after ignoring
                tree.append(
                    {
                        "path": full_path,
                        "name": entry,
                        "type": "folder",
                        "children": subtree,
                    }
                )
        else:
            tree.append({"path": full_path, "name": entry, "type": "file"})
    return tree


def display_tree(tree, selected_paths, level=0):
    """
    Recursively display the file/folder tree in Streamlit with indentation
    and checkboxes for file selection.
    """
    for item in tree:
        # Create an indented label for nesting
        indent = "&nbsp;" * (level * 4)  # Use HTML non-breaking spaces for indentation
        if item["type"] == "folder":
            # Display folder name as bold text
            st.markdown(f"{indent}**{item['name']}**", unsafe_allow_html=True)
            # Recursively display its children with increased indentation
            display_tree(item["children"], selected_paths, level + 1)
        else:
            # Display checkbox for files
            label = f"{indent}{item['name']}"
            checked = st.checkbox(label, key=item["path"])
            if checked:
                selected_paths.add(item["path"])


def generate_markdown(selected_paths):
    """
    Reads the content of the selected files and concatenates them into one
    Markdown string. You can customize formatting as needed.

    Parameters:
    - selected_paths: A set of file paths selected by the user.

    Returns:
    - A string containing the combined Markdown content.
    """
    md_content = []
    for path in sorted(selected_paths):
        # Append a heading with file name
        md_content.append(f"## {os.path.basename(path)}\n")
        # Determine the language for syntax highlighting based on file extension
        _, ext = os.path.splitext(path)
        language = ext[1:] if ext else ""
        md_content.append(f"```{language}\n")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                md_content.append(f.read())
        except Exception as e:
            md_content.append(f"Error reading file: {e}\n")
        md_content.append("```\n")
    return "\n".join(md_content)


def main():
    st.title("Markdown Generator from Project Files")
    st.write(
        "Specify a directory to scan, respecting `.gitignore`. Then choose files to include."
    )

    # 1. Input for directory path
    project_path = st.text_input(
        "Project Directory Path",
        value="",
        help="Enter the absolute path to your project.",
    )

    if project_path and os.path.isdir(project_path):
        # 2. Load .gitignore if exists
        gitignore_path = os.path.join(project_path, ".gitignore")
        spec = load_gitignore_patterns(gitignore_path)

        if spec:
            st.info("`.gitignore` patterns loaded and will be respected.")
        else:
            st.warning(
                "No `.gitignore` found or it's empty. All files will be included."
            )

        # 3. Gather file tree
        tree = gather_files_and_folders(project_path, spec)

        if not tree:
            st.warning("No files or folders found to display.")
        else:
            # 4. Display the tree in checkboxes
            selected_paths = set()
            display_tree(tree, selected_paths)

            # 5. Button to generate Markdown
            if st.button("Generate Markdown"):
                if not selected_paths:
                    st.error(
                        "No files selected. Please select at least one file to generate Markdown."
                    )
                else:
                    # Generate the content
                    result = generate_markdown(selected_paths)

                    # 6. Save to a file (e.g., OUTPUT.md)
                    app_directory = os.path.dirname(os.path.abspath(__file__))
                    output_file = os.path.join(app_directory, "OUTPUT.md")
                    try:
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(result)
                        st.success(f"Markdown file generated at: `{output_file}`")
                        st.download_button(
                            label="Download Markdown",
                            data=result,
                            file_name="OUTPUT.md",
                            mime="text/markdown",
                        )
                    except Exception as e:
                        st.error(f"Failed to write Markdown file: {e}")
    elif project_path:
        st.error("The provided path does not exist or is not a directory.")


if __name__ == "__main__":
    main()
