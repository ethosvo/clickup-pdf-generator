# ClickUp PDF Generator

Generate beautifully formatted PDFs from ClickUp task data (`task_data.json`) or directly via the ClickUp API.

This project decodes ClickUp JSON (including **Quill rich-text fields**, **Markdown descriptions**, hyperlinks, and custom IDs) into a styled PDF report.  
It renders task references as **button-like links** and maintains proper styling across sections.

---

## 🔧 Project Structure (post-refactor)

The project now uses a **src layout** with two top-level packages: `cli` (entrypoints) and `pdf_generator` (core logic).

```
clickup-pdf-generator/
├─ pyproject.toml                # modern packaging config, defines console script
├─ .env                          # environment variables (not committed)
├─ outputs/                      # generated JSON + PDF files
├─ src/
│  ├─ cli/
│  │  ├─ __init__.py
│  │  └─ make_pdfs.py            # CLI entrypoint (console script: make-pdfs)
│  └─ pdf_generator/
│     ├─ __init__.py
│     ├─ renderers.py            # build_story() for PDF layout
│     ├─ services/
│     │  └─ task_loader.py
│     ├─ pdf/
│     │  └─ generator.py
│     └─ core/
│        ├─ config.py
│        └─ paths.py
└─ README.md
```

---

## 🚀 Usage

### 1. Environment

Create a `.env` file in the project root with your API key and (optionally) default team:

```env
CLICKUP_API_KEY=your_api_key_here
CLICKUP_TEAM_ID=20419954   # optional fallback for custom IDs
```

Install in editable/development mode:

```bash
python -m pip install -e .
```

---

### 2. One-click wrapper (multi-task)

Fetch **one or more tasks** and generate **paired JSON+PDF** into the `outputs/` folder.  
Files are numbered sequentially (persistent across runs), and JSON/PDF share the same basename.

Examples:

```bash
# Using console script
make-pdfs PERSON-20340

# Multiple IDs
make-pdfs PERSON-20340 8699x95rb 9012345678

# Explicit team
make-pdfs PERSON-20340 --team 20419954

# Full URL (team auto-detected)
make-pdfs "https://app.clickup.com/t/20419954/PERSON-20340"

# Override API key and skip markdown description
make-pdfs PERSON-20340   --api-key sk_xxxxx   --no-markdown
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
- Preserves **Markdown task descriptions**, including headings, bullet lists, bold/italic, and hyperlinks.
- Replaces `[id] ClickUp Task` placeholders with proper `[custom_id] Name` buttons.
- Renders contributors, owners, and linked tasks as pill-shaped buttons.
- Maintains consistent ReportLab styles across sections.
- Safe filenames for all outputs.

---

## 🛠 Requirements

- Python 3.9+
- Dependencies: `reportlab`, `python-dotenv`, `requests`

---

## 🧑‍💻 Development Workflow

Typical Git workflow:

```bash
git pull origin main
git checkout -b feature/refactor-src-layout
git add .
git commit -m "Refactor to src layout with cli/pdf_generator packages"
git push origin feature/refactor-src-layout
```

---

## 🔮 Future Enhancements

- OAuth and FastAPI web UI for task selection
- More robust Quill decoding (images, embeds, banners).
- Unit tests for parser/renderers.
- Support for additional ClickUp slash-command formatting.

---

## 📜 Commit Notes

**One-line commit message:**
```
Refactor to src layout with cli/pdf_generator packages and working console script
```

**Detailed description:**
```
- Migrated project to a src/ layout for cleaner packaging
- Split code into two packages: cli/ for entrypoints and pdf_generator/ for core logic
- Added pyproject.toml with setuptools configuration and console script definition
- Ensured __init__.py files across all subpackages
- Updated make_pdfs.py to import via pdf_generator.* absolute imports
- Verified editable install works with `pip install -e .`
- Confirmed console script `make-pdfs` executes successfully and generates JSON/PDF pairs
```
