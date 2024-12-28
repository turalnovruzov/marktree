# MarkTree

MarkTree is a lightweight and intuitive tool for generating Markdown files from your project's source code. It lets you explore your project directory, respect `.gitignore` patterns, and selectively include files or folders in a Markdown summary.

---

## 🚀 Features

- **Interactive File Tree**: Visualize your project structure with an expandable file tree.
- **Selective Inclusion**: Choose specific files and folders to include in the generated Markdown.
- **Respects `.gitignore`**: Automatically excludes files and folders listed in `.gitignore`.
- **Explicit `.git` Exclusion**: Always skips the `.git` folder to avoid unnecessary clutter.
- **Syntax Highlighting**: Automatically adds syntax highlighting for code blocks based on file extensions.
- **One-Click Markdown**: Generate and download your Markdown summary with a single click.

---

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/marktree.git
   cd marktree
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

1. Start the app:

   ```bash
   streamlit run app.py
   ```

2. Open your browser at `http://localhost:8501`.

3. Enter the path to your project's root directory.

4. Explore the file tree and select the files and folders you want to include.

5. Click the **Generate Markdown** button to create your Markdown file.

6. Download the file or view it directly in the browser!

---

## 📂 File Structure

```
MarkTree/
├── app.py                 # Main application code
├── requirements.txt       # Dependencies
├── README.md              # This file
```

---

## 📝 Example Markdown Output

Given the following file tree:

```
src/
├── main.py
├── utils/
│   ├── helper.py
│   └── constants.py
```

The generated Markdown might look like this:

````markdown
## main.py

```python
# Main script content here
print("Hello, world!")
```

## helper.py

```python
# Helper functions
def greet(name):
    return f"Hello, {name}!"
```

## constants.py

```python
# Constants
PI = 3.14159
```
````

---

## 🤝 Contributions

Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## 📃 License

This project is licensed under the [MIT License](LICENSE).

---

## 💡 Future Enhancements

- Directory picker for user-friendly navigation.
- Configurable output formatting options.
- Support for additional file types and custom exclusions.

---

## 🌟 Acknowledgments

Built with ❤️ using [Streamlit](https://streamlit.io/) and [PathSpec](https://pypi.org/project/pathspec/).
