## ClickUp PDF Generator

This script extracts data from a ClickUp task (via JSON export) and generates a neatly formatted PDF summary for value exchange reviews.

### Current Functionality (v1 milestone)
- Reads structured task data from `task_data.json`
- Outputs `clickup_task_output.pdf` with:
  - Title, task URL, and email/contact fields
  - All non-empty custom fields
  - Rich text rendered with basic formatting (bold, italic, links, line breaks)
  - People fields (e.g. Owner, Contributors, Wellbeing Mentor) listed cleanly by name
- Ignores irrelevant system metadata (internal IDs, colors, status codes)
- Automatically overwrites PDF on each run

### Setup
1. Install dependencies:
   ```bash
   pip install reportlab
Place your task_data.json file in the project root.

Run:

bash
Copy
Edit
python generate_pdf.py
Next Steps (planned)
Support for badges, highlights, nested lists

Better support for ClickUp rich formatting: headings, dividers, embedded tasks