import json
from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.lib.units import inch
from utils import urlify_text, TASK_BRACKET_RE

def replace_brackets_with_buttons(text, task_lookup, make_button, styles):
    flows = []
    parts = TASK_BRACKET_RE.split(text)
    for part in parts:
        m = TASK_BRACKET_RE.match(part)
        if m:
            tid = m.group(1)
            custom_id, name = task_lookup.get(tid, (tid, "ClickUp Task"))
            url = f"https://app.clickup.com/t/{tid}"
            flows.append(make_button(f"[{custom_id}] {name}", url))
            flows.append(Spacer(1, 4))
        else:
            if part.strip():
                flows.append(Paragraph(urlify_text(part, task_lookup), styles['NormalText']))
    return flows

def render_quill_ops(ops, task_lookup, make_button, styles):
    flows = []
    text_buffer = ""
    for op in ops:
        insert = op.get("insert")
        if isinstance(insert, dict) and "task_mention" in insert:
            mention = insert["task_mention"]
            task_id = mention.get("task_id", "")
            custom_id = mention.get("custom_id") or task_id
            name = mention.get("name") or "ClickUp Task"
            if task_id:
                link = f"https://app.clickup.com/t/{task_id}"
                flows.append(make_button(f"[{custom_id}] {name}", link))
                flows.append(Spacer(1, 4))
            continue
        if isinstance(insert, dict) and "image" in insert:
            img_url = insert["image"]
            try:
                flows.append(Image(img_url, width=2*inch, height=2*inch))
            except Exception:
                flows.append(Paragraph(f"[Image: {img_url}]", styles['NormalText']))
            continue
        if isinstance(insert, str):
            text_buffer += insert
    if text_buffer:
        flows.extend(replace_brackets_with_buttons(text_buffer, task_lookup, make_button, styles))
    return flows
