ClickUp PDF Generator

Generate beautifully formatted PDFs from ClickUp task data (`task_data.json`).

This project decodes ClickUp JSON (including Quill rich-text fields, hyperlinks, and custom IDs) into a styled PDF report.  
It renders task references as **button-like links** and maintains proper styling across sections.

---

## 🔧 Project Structure
clickup-pdf-generator/
│
├── generate_pdf.py # Main entrypoint
├── styles.py # ReportLab style definitions
├── utils.py # Helpers: regex, filenames, URL parsing
├── clickup_parser.py # Decode Quill ops, bracketed task refs
├── renderers.py # Button/people/field renderers
├── task_data.json # Example input (ClickUp export)
└── README.md

yaml
Copy
Edit

---

## 🚀 Usage

1. Export your ClickUp task data as `task_data.json` and place it in this folder.
2. Run:

   ```bash
   python generate_pdf.py
The script generates a PDF named after the task (safe filename).

✨ Features
Parses Quill Delta rich text (value_richtext) from ClickUp.

Replaces [id] ClickUp Task placeholders with proper [custom_id] Name buttons.

Renders contributors, owners, and linked tasks as pill-shaped buttons.

Maintains consistent ReportLab styles across sections.

Automatically sanitizes filenames for safe saving.

🛠 Requirements
Python 3.9+

Install dependencies:

bash
Copy
Edit
pip install reportlab
📌 Notes
generate_pdf.py is the entrypoint — the rest are modularized for clarity.

If you want to customize fonts/colors, edit styles.py.

Future enhancements:

More robust Quill decoding (images, embeds).

Unit tests for parser functions.

🧑‍💻 Development
Typical workflow with Git:

bash
Copy
Edit
# Pull latest
git pull origin main

# Work on changes
code .

# Stage & commit
git add .
git commit -m "Refactor: modularize PDF generator (styles, utils, parser, renderers)"

# Push to GitHub
git push origin main