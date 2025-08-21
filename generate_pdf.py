from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
import json
import os

# Load JSON data
with open("task_data.json", "r", encoding="utf-8") as f:
    task_data = json.load(f)

# Set PDF file name
pdf_filename = "clickup_task_output.pdf"

# Create document
doc = SimpleDocTemplate(pdf_filename, pagesize=LETTER)
styles = getSampleStyleSheet()
elements = []

def add_heading(text):
    elements.append(Paragraph(f"<b>{text}</b>", styles['Heading4']))
    elements.append(Spacer(1, 8))

def add_text(text):
    elements.append(Paragraph(text, styles['BodyText']))
    elements.append(Spacer(1, 6))

def format_people_list(title, people):
    add_heading(title)
    if isinstance(people, list):
        for person in people:
            name = person.get("name", "Unknown")
            url = person.get("url", "")
            if url:
                link = f'<a href="{url}">{name}</a>'
            else:
                link = name
            add_text(f"• {link}")
    else:
        add_text("None listed")

# Title
add_heading(f"Task: {task_data.get('name', 'Unnamed Task')}")

# Custom Fields
add_heading("Custom Fields:")
custom_fields = task_data.get("custom_fields", [])
for field in custom_fields:
    name = field.get("name", "Unnamed Field")
    value = field.get("value", "")
    if isinstance(value, list) and value and isinstance(value[0], dict) and "name" in value[0] and "url" in value[0]:
        format_people_list(name, value)
    else:
        add_text(f"{name}: {value}")

# Generate PDF
doc.build(elements)
print(f"✅ PDF generated at: {os.path.abspath(pdf_filename)}")
