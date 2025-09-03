# ClickUp PDF Generator

Generate beautifully formatted PDFs from ClickUp task data (`task_data.json`).

This project decodes ClickUp JSON (including **Quill rich-text fields**, **Markdown descriptions**, hyperlinks, and custom IDs) into a styled PDF report.  
It renders task references as **button-like links** and maintains proper styling across sections.

---

## 🔧 Project Structure

- `fetch_clickup_task.py` – Fetch a single task JSON via ClickUp API
- `generate_pdf.py` – Entrypoint for PDF generation from JSON
- `make_pdfs.py` – **NEW** wrapper: fetch **one or more tasks** and auto-generate paired JSON+PDF in `outputs/`
- `clickup_parser.py` – Decode Quill ops, bracketed task refs
- `renderers.py` – Render description + fields (rich or plain)
- `styles.py` – ReportLab style definitions
- `utils.py` – Helpers: regex, filenames, URL parsing
- `README.md`

---

## 🚀 Usage

### 1. Environment

Create a `.env` file in the project root with your API key and (optionally) default team:

```env
CLICKUP_API_KEY=your_api_key_here
CLICKUP_TEAM_ID=20419954   # optional fallback for custom IDs
```

Install dependencies:

```bash
pip install reportlab python-dotenv requests
```

---

### 2. Classic workflow (single task)

Fetch a task into JSON:
```bash
python fetch_clickup_task.py PERSON-20340 --team 20419954
# → writes task_data.json
```

Generate PDF from JSON:
```bash
python generate_pdf.py
# → writes <taskname>.pdf
```

---

### 3. One-click wrapper (multi-task)

Fetch **one or more tasks** and generate **paired JSON+PDF** into the `outputs/` folder.  
Files are numbered sequentially (persistent across runs), and JSON/PDF share the same basename.

Examples:

```bash
# Single custom ID (team picked up from .env if not supplied)
python make_pdfs.py PERSON-20340

# Multiple IDs in one call (mix of custom and numeric)
python make_pdfs.py PERSON-20340 8699x95rb 9012345678

# With explicit team
python make_pdfs.py PERSON-20340 --team 20419954

# From a full URL (team auto-detected)
python make_pdfs.py "https://app.clickup.com/t/20419954/PERSON-20340"

# Override API key and skip markdown description
python make_pdfs.py PERSON-20340   --api-key sk_xxxxx   --no-markdown
```

Output structure:
```
outputs/
├─ 0007 - PERSON-20340__Task_Title.json
├─ 0007 - PERSON-20340__Task_Title.pdf
├─ 0008 - 8699x95rb__Other_Task.json
├─ 0008 - 8699x95rb__Other_Task.pdf
```

---

## ✨ Features

- Parses **Quill Delta rich text** (`value_richtext`) from custom fields.
- Preserves **Markdown task descriptions**, including:
  - Headings, bullet lists, bold/italic text, and hyperlinks.
- Replaces `[id] ClickUp Task` placeholders with proper `[custom_id] Name` buttons.
- Renders contributors, owners, and linked tasks as pill-shaped buttons.
- Maintains consistent ReportLab styles across sections.
- Safe filenames for all outputs.

---

## 🛠 Requirements

- Python 3.9+
- Dependencies: `reportlab`, `python-dotenv`, `requests`

---

## 🧑‍💻 Development

Typical Git workflow:

```bash
git pull origin main
git checkout -b feature/new-option
git add .
git commit -m "Add new feature"
git push origin feature/new-option
```

---

## 🔮 Future Enhancements

- More robust Quill decoding (images, embeds, banners).
- Unit tests for parser/renderers.
- Support for additional ClickUp slash-command formatting.
