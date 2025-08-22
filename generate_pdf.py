import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors

# Load task data
with open("task_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract task metadata
task_name = data.get("name", "Untitled Task")
task_url = data.get("url", "")
custom_fields = data.get("custom_fields", [])

# Set up PDF doc
pdf_filename = "clickup_task_output.pdf"
doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=60,
    bottomMargin=60
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, leading=18, spaceAfter=6, spaceBefore=12, textColor=colors.darkblue, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='NormalText', fontSize=10, leading=14, alignment=TA_LEFT))

elements = []

# Header
elements.append(Paragraph(f"<b>{task_name}</b>", styles['Title']))
if task_url:
    elements.append(Paragraph(f"<a href='{task_url}'>{task_url}</a>", styles['Normal']))
elements.append(Spacer(1, 0.25 * inch))

# Helper function for formatting people fields
def format_people(people_list):
    names = []
    for person in people_list:
        name = person.get("name", "")
        if name:
            names.append(f"• {name}")
    return "<br/>".join(names) if names else ""

# Add all custom fields with values
for field in custom_fields:
    title = field.get("name", "").strip()
    value = field.get("value")
    rich_text_ops = field.get("value_richtext")

    if not value and not rich_text_ops:
        continue  # skip empty fields

    elements.append(Paragraph(title, styles['SectionTitle']))

    # Handle rich text (basic formatting for now)
    if isinstance(rich_text_ops, str):
        try:
            ops = json.loads(rich_text_ops).get("ops", [])
            text_chunks = []
            for op in ops:
                insert = op.get("insert", "")
                attrs = op.get("attributes", {})
                if "bold" in attrs:
                    insert = f"<b>{insert}</b>"
                if "italic" in attrs:
                    insert = f"<i>{insert}</i>"
                if "link" in attrs:
                    insert = f"<a href='{attrs['link']}'>{insert.strip()}</a>"
                insert = insert.replace("\n", "<br/>")
                text_chunks.append(insert)
            final_text = "".join(text_chunks)
            elements.append(Paragraph(final_text, styles['NormalText']))
        except Exception as e:
            elements.append(Paragraph(str(value), styles['NormalText']))
    elif isinstance(value, list) and value and isinstance(value[0], dict) and "name" in value[0]:
        formatted_people = format_people(value)
        elements.append(Paragraph(formatted_people, styles['NormalText']))
    elif isinstance(value, str):
        elements.append(Paragraph(value.strip(), styles['NormalText']))
    elif isinstance(value, dict) and "name" in value:
        elements.append(Paragraph(value["name"], styles['NormalText']))

    elements.append(Spacer(1, 0.2 * inch))

# Write PDF
doc.build(elements)
print(f"✅ PDF generated: {pdf_filename}")
