# ClickUp PDF Generator

Generate beautifully formatted PDFs from ClickUp task data (`task_data.json`).

This project decodes ClickUp JSON (including **Quill rich-text fields**, **Markdown descriptions**, hyperlinks, and custom IDs) into a styled PDF report.  
It renders task references as **button-like links** and maintains proper styling across sections.

---

## 🔧 Project Structure
clickup-pdf-generator/
│
├── fetch_clickup_task.py   # Fetch task JSON via ClickUp API (with markdown_description)
├── generate_pdf.py         # Entrypoint for PDF generation
├── clickup_parser.py       # Decode Quill ops, bracketed task refs
├── renderers.py            # Render description + fields (rich or plain)
├── styles.py               # ReportLab style definitions
├── utils.py                # Helpers: regex, filenames, URL parsing
├── task_data.json          # Example input (ClickUp export)
└── README.md

---

## 🚀 Usage

1. Set your ClickUp API key in `.env`:
   ```env
   CLICKUP_API_KEY=your_api_key_here
   ```

2. Edit `fetch_clickup_task.py` with your task URL and run to fetch JSON:
   ```bash
   python fetch_clickup_task.py
   ```

   This will create `task_data.json`.  
   ✅ Includes `markdown_description` thanks to `include_markdown_description=true`.

3. Generate a PDF from the JSON:
   ```bash
   python generate_pdf.py
   ```

   The script generates a PDF named after the task (safe filename).

---

## ✨ Features

- Parses **Quill Delta rich text** (`value_richtext`) from custom fields.
- Preserves **Markdown task descriptions** (`markdown_description`), including:
  - Headings (`#`, `##`, `###`)
  - Bullet lists (`-`, `*`)
  - **Bold**, *italic*, and [links](url)
- Replaces `[id] ClickUp Task` placeholders with proper `[custom_id] Name` buttons.
- Renders contributors, owners, and linked tasks as pill-shaped buttons.
- Maintains consistent ReportLab styles across sections.
- Automatically sanitizes filenames for safe saving.

---

## 🛠 Requirements

- Python 3.9+
- Dependencies:
  ```bash
  pip install reportlab python-dotenv requests
  ```

---

## 📌 Notes

- `fetch_clickup_task.py` must be run first to populate `task_data.json`.
- `generate_pdf.py` is the entrypoint — the rest are modularized for clarity.
- If you want to customize fonts/colors, edit `styles.py`.

---

## 🧑‍💻 Development

Typical workflow with Git:

```bash
# Pull latest
git pull origin main

# Create a feature branch
git checkout -b feature/markdown-description

# Stage & commit
git add .
git commit -m "Enhancement: support markdown_description and improve rich text rendering"

# Push to GitHub
git push origin feature/markdown-description

# Merge into main via PR
```

---

## 🔮 Future Enhancements

- More robust Quill decoding (images, embeds, banners).
- Unit tests for parser/renderers.
- Support for additional ClickUp slash-command formatting (badges, dividers, YouTube embeds).
