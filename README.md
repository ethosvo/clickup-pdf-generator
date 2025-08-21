# ClickUp PDF Generator

This project is a lightweight, code-only solution for generating well-formatted PDFs from ClickUp data (e.g. tasks, comments, custom fields). It is designed to work offline and free of licensing costs, using open-source Python libraries.

## Features

- Pull data from ClickUp (via JSON or API)
- Format data into clean, readable PDF reports
- Use ReportLab or WeasyPrint for PDF generation
- Fully automated via CLI or script

## Requirements

- Python 3.8+
- pip

## Setup

```bash
git clone https://github.com/ethosvo/clickup-pdf-generator.git
cd clickup-pdf-generator
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt

Usage
python generate_pdf.py data/example.json

License

MIT License


---

### ✅ `.gitignore` (for Python project on Windows)

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
ENV/
env/
.venv/
*.env

# VS Code settings
.vscode/

# Distribution / packaging
build/
dist/
*.egg-info/

# Log files
*.log

# OS-specific
.DS_Store
Thumbs.db
