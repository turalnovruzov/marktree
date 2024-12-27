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
    
    with open(gitignore_path, 'r') as f:
        gitignore_contents = f.read().splitlines()
    
    # Create a PathSpec from the read patterns
    spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_contents)
    return spec

def gather_files_and_folders(root_path, spec=None):
    """
    Recursively gather all files and folders from root_path,
    excluding those matched by the .gitignore spec if present.
    Returns a nested list/dict structure for the tree.
    """
    tree = []

    # Sort entries for consistent ordering
    entries = sorted(os.listdir(root_path))

    for entry in entries:
        full_path = os.path.join(root_path, entry)
        
        # Relative path for ignore matching
        rel_path = os.path.relpath(full_path, start=root_path)
        
        # If we have a spec and this path is ignored, skip it
        if spec and spec.match_file(rel_path):
            continue
        
        # Build a dictionary structure
        if os.path.isdir(full_path):
            # Recursively gather subfolders
            subtree = gather_files_and_folders(full_path, spec)
            if subtree:  # If folder not empty after ignoring
                tree.append({
                    'path': full_path,
                    'name': entry,
                    'type': 'folder',
                    'children': subtree
                })
        else:
            tree.append({
                'path': full_path,
                'name': entry,
                'type': 'file'
            })
    return tree

def display_tree(tree, selected_paths, level=0):
    """
    Recursively display the file/folder tree in Streamlit with checkboxes.
    Adds selected items to selected_paths set when checked.
    Uses indentation for nested levels instead of nested expanders.
    """
    for item in tree:
        # Create an indented label for nesting
        label = "  " * level + item['name']

        if item['type'] == 'folder':
            # Use a header or markdown for folder names instead of expander
            st.markdown(f"**{label}**")
            # Recursively display its children with increased indentation
            display_tree(item['children'], selected_paths, level + 1)
        else:
            # Display checkbox for files
            checked = st.checkbox(label, key=item['path'])
            if checked:
                selected_paths.add(item['path'])

def generate_markdown(selected_paths):
    """
    Reads the content of the selected files and concatenates them into one
    Markdown string. You can customize formatting as needed.
    """
    md_content = []
    for path in sorted(selected_paths):
        # Append a heading with file name (optional)
        md_content.append(f"## {os.path.basename(path)}\n")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            md_content.append(f"```\n{f.read()}\n```\n")
    return "\n".join(md_content)

def main():
    st.title("Markdown Generator from Project Files")
    st.write("Specify a directory to scan, respecting `.gitignore`. Then choose files to include.")

    # 1. Input for directory path
    project_path = st.text_input("Project Directory Path", value="", help="Enter the absolute path to your project.")
    
    if project_path and os.path.isdir(project_path):
        # 2. Load .gitignore if exists
        gitignore_path = os.path.join(project_path, ".gitignore")
        spec = load_gitignore_patterns(gitignore_path)
        
        # 3. Gather file tree
        tree = gather_files_and_folders(project_path, spec)
        
        # 4. Display the tree in checkboxes
        selected_paths = set()
        display_tree(tree, selected_paths)

        # 5. Button to generate Markdown
        if st.button("Generate Markdown"):
            # Generate the content
            result = generate_markdown(selected_paths)
            
            # 6. Save to a file (e.g., OUTPUT.md)
            output_file = os.path.join(project_path, "OUTPUT.md")
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(result)
            
            st.success(f"Markdown file generated at: {output_file}")
            st.download_button(
                label="Download Markdown",
                data=result,
                file_name="OUTPUT.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()