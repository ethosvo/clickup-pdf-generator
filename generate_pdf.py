import json
import re
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

# Generate a safe filename from task name
safe_task_name = re.sub(r'[^\w\s-]', '', task_name)
safe_task_name = re.sub(r'\s+', '_', safe_task_name).strip('_')
pdf_filename = f"{safe_task_name}.pdf"

doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=60,
    bottomMargin=60
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, leading=18,
                          spaceAfter=6, spaceBefore=12,
                          textColor=colors.darkblue, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='NormalText', fontSize=10, leading=14,
                          alignment=TA_LEFT))

elements = []

# Regex to detect plain URLs in text
URL_RE = re.compile(r'(https?://\S+)', re.IGNORECASE)

def urlify_text(text: str) -> str:
    """Wrap plain URLs in anchor tags and preserve line breaks."""
    def repl(match):
        url = match.group(1).rstrip(').,;')
        return f"<a href='{url}'>{url}</a>"
    text = URL_RE.sub(repl, text or '')
    text = text.replace("\n", "<br/>")
    return text

# Header
elements.append(Paragraph(f"<b>{task_name}</b>", styles['Title']))
if task_url:
    elements.append(Paragraph(f"<a href='{task_url}'>{task_url}</a>", styles['Normal']))
elements.append(Spacer(1, 0.25 * inch))

# Helper function for formatting people fields
def format_people(people_list):
    chunks = []
    for person in people_list or []:
        name = person.get("name", "").strip()
        url = person.get("url", "").strip()
        if not name:
            continue
        if url:
            chunks.append(f"• <a href='{url}'>{name}</a>")
        else:
            chunks.append(f"• {name}")
    return "<br/>".join(chunks) if chunks else ""

def render_value(field_value, rich_text_ops):
    """Return a list of Flowables (Paragraphs/Spacers) to render this field."""
    flows = []

    # Handle rich text first
    if isinstance(rich_text_ops, str):
        try:
            ops = json.loads(rich_text_ops).get("ops", [])
            text_chunks = []
            for op in ops:
                insert = op.get("insert", "")
                attrs = op.get("attributes", {}) or {}

                # Handle task mentions
                if isinstance(insert, dict) and "task_mention" in insert:
                    task_id = insert["task_mention"].get("task_id", "")
                    if task_id:
                        link = f"https://app.clickup.com/t/{task_id}"
                        insert_text = attrs.get("text", "ClickUp Task")
                        insert = f"<a href='{link}'>{insert_text}</a>"
                    else:
                        insert = ""

                # Normal string inserts
                elif isinstance(insert, str):
                    insert = insert.replace("\n", "<br/>")
                    if attrs.get("bold"):
                        insert = f"<b>{insert}</b>"
                    if attrs.get("italic"):
                        insert = f"<i>{insert}</i>"
                    if "link" in attrs:
                        link = attrs["link"]
                        visible = insert.strip() or link
                        insert = f"<a href='{link}'>{visible}</a>"
                else:
                    insert = ""

                text_chunks.append(insert)

            final_text = "".join(text_chunks)
            flows.append(Paragraph(final_text, styles['NormalText']))
            return flows
        except Exception:
            pass  # fall through to other handlers if parsing fails

    # People arrays
    if isinstance(field_value, list) and field_value and isinstance(field_value[0], dict) and "name" in field_value[0]:
        flows.append(Paragraph(format_people(field_value), styles['NormalText']))
        return flows

    # Single dict (one related item/person)
    if isinstance(field_value, dict) and "name" in field_value:
        name = field_value.get("name", "")
        url = field_value.get("url", "")
        if url:
            flows.append(Paragraph(f"<a href='{url}'>{name}</a>", styles['NormalText']))
        else:
            flows.append(Paragraph(name, styles['NormalText']))
        return flows

    # Plain strings
    if isinstance(field_value, str):
        flows.append(Paragraph(urlify_text(field_value.strip()), styles['NormalText']))
        return flows

    # Fallback
    flows.append(Paragraph(str(field_value), styles['NormalText']))
    return flows

# Add all custom fields with values
for field in custom_fields:
    title = field.get("name", "").strip()
    value = field.get("value")
    rich_text_ops = field.get("value_richtext")

    if (value in (None, "", [], {})) and not rich_text_ops:
        continue  # skip empty fields

    elements.append(Paragraph(title, styles['SectionTitle']))
    for flow in render_value(value, rich_text_ops):
        elements.append(flow)
    elements.append(Spacer(1, 0.2 * inch))

# Write PDF
doc.build(elements)
print(f"✅ PDF generated: {pdf_filename}")
