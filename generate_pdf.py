import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from styles import get_styles
from utils import safe_filename
from renderers import render_value

# Load task data
with open("task_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

task_name = data.get("name", "Untitled Task")
task_url = data.get("url", "")
custom_fields = data.get("custom_fields", [])

# Build lookup dict for resolving IDs (by id and by custom id)
task_lookup = {}
def index_people(field):
    if isinstance(field, list):
        for p in field:
            tid = p.get("id")
            cid = p.get("custom_id") or tid
            name = p.get("name", "")
            if tid:
                task_lookup[tid] = (cid, name)
            if cid:
                task_lookup[cid] = (cid, name)
    elif isinstance(field, dict):
        tid = field.get("id")
        cid = field.get("custom_id") or tid
        name = field.get("name", "")
        if tid:
            task_lookup[tid] = (cid, name)
        if cid:
            task_lookup[cid] = (cid, name)

for cf in custom_fields:
    val = cf.get("value")
    if val:
        index_people(val)

# Also index the current task itself by id and custom id
this_id = data.get("id")
this_cust = data.get("custom_id") or this_id
if this_id:
    task_lookup[this_id] = (this_cust, task_name)
if this_cust:
    task_lookup[this_cust] = (this_cust, task_name)

# File naming
safe_task_name = safe_filename(task_name)
pdf_filename = f"{safe_task_name}.pdf"

doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                        rightMargin=40, leftMargin=40,
                        topMargin=60, bottomMargin=60)

styles = get_styles()
elements = []

elements.append(Paragraph(f"<b>{task_name}</b>", styles['Title']))
if task_url:
    elements.append(Paragraph(f"<a href='{task_url}'>{task_url}</a>", styles['NormalText']))
elements.append(Spacer(1, 0.25 * 72))

for field in custom_fields:
    title = field.get("name", "").strip()
    value = field.get("value")
    rich_text_ops = field.get("value_richtext")
    if (value in (None, "", [], {})) and not rich_text_ops:
        continue
    elements.append(Paragraph(title, styles['SectionTitle']))
    for flow in render_value(value, rich_text_ops, task_lookup, styles):
        elements.append(flow)
    elements.append(Spacer(1, 0.2 * 72))

doc.build(elements)
print(f"✅ PDF generated: {pdf_filename}")
