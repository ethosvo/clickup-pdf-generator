import json
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepInFrame
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
# Softer grey pill-button style with spacing
styles.add(ParagraphStyle(name='ButtonLink',
                          fontSize=9,
                          leading=11,
                          textColor=colors.black,
                          backColor=colors.whitesmoke,
                          borderColor=colors.grey,
                          borderWidth=0.5,
                          borderRadius=6,
                          borderPadding=(2, 6, 2, 6),
                          spaceAfter=6,
                          spaceBefore=2,
                          alignment=TA_LEFT))

elements = []

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
    elements.append(Paragraph(f"<a href='{task_url}'>{task_url}</a>", styles['NormalText']))
elements.append(Spacer(1, 0.25 * inch))

def resolve_id(obj: dict) -> str:
    """Return custom_id if available, else fallback to id."""
    return obj.get("custom_id") or obj.get("id", "")

def make_button(label: str, url: str):
    """Return a pill-style button that shrink-wraps to content."""
    p = Paragraph(f"<a href='{url}'>{label}</a>", styles['ButtonLink'])
    # Limit width so it never spans full page
    return KeepInFrame(maxWidth=3*inch, maxHeight=0, content=[p], hAlign='LEFT')

def format_people(people_list):
    flows = []
    for person in people_list or []:
        name = person.get("name", "").strip()
        url = person.get("url", "").strip()
        tid = resolve_id(person)
        if not name:
            continue
        if url and tid:
            label = f"[{tid}] {name}"
            flows.append(make_button(label, url))
        elif url:
            flows.append(make_button(name, url))
        else:
            flows.append(Paragraph(name, styles['NormalText']))
    return flows

def render_value(field_value, rich_text_ops):
    flows = []
    # Handle rich text with task mentions
    if isinstance(rich_text_ops, str):
        try:
            ops = json.loads(rich_text_ops).get("ops", [])
            text_chunks = []
            for op in ops:
                insert = op.get("insert", "")
                attrs = op.get("attributes", {}) or {}
                if isinstance(insert, dict) and "task_mention" in insert:
                    task_id = insert["task_mention"].get("task_id", "")
                    custom_id = insert["task_mention"].get("custom_id")
                    disp_id = custom_id or task_id
                    if task_id:
                        link = f"https://app.clickup.com/t/{task_id}"
                        label = f"[{disp_id}] ClickUp Task"
                        flows.append(make_button(label, link))
                        continue
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
                    text_chunks.append(insert)
            if text_chunks:
                final_text = "".join(text_chunks)
                flows.append(Paragraph(final_text, styles['NormalText']))
            return flows
        except Exception:
            pass

    if isinstance(field_value, list) and field_value and isinstance(field_value[0], dict) and "name" in field_value[0]:
        flows.extend(format_people(field_value))
        return flows

    if isinstance(field_value, dict) and "name" in field_value:
        name = field_value.get("name", "")
        url = field_value.get("url", "")
        tid = resolve_id(field_value)
        if url and tid:
            label = f"[{tid}] {name}"
            flows.append(make_button(label, url))
        elif url:
            flows.append(make_button(name, url))
        else:
            flows.append(Paragraph(name, styles['NormalText']))
        return flows

    if isinstance(field_value, str):
        flows.append(Paragraph(urlify_text(field_value.strip()), styles['NormalText']))
        return flows

    flows.append(Paragraph(str(field_value), styles['NormalText']))
    return flows

# Build PDF
for field in custom_fields:
    title = field.get("name", "").strip()
    value = field.get("value")
    rich_text_ops = field.get("value_richtext")
    if (value in (None, "", [], {})) and not rich_text_ops:
        continue
    elements.append(Paragraph(title, styles['SectionTitle']))
    for flow in render_value(value, rich_text_ops):
        elements.append(flow)
    elements.append(Spacer(1, 0.2 * inch))

doc.build(elements)
print(f"✅ PDF generated: {pdf_filename}")
