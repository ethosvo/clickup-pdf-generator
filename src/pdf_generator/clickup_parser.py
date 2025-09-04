import json
from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.lib.units import inch
from pdf_generator.utils import urlify_text, TASK_BRACKET_RE, TASK_ANY_URL_RE

def build_lookup_from_richtext(custom_fields, task_lookup: dict):
    """Scan all value_richtext fields to index task mentions and link texts by id OR custom id."""
    for cf in custom_fields:
        r = cf.get("value_richtext")
        if not isinstance(r, str):
            continue
        try:
            ops = json.loads(r).get("ops", [])
        except Exception:
            continue
        for op in ops:
            insert = op.get("insert")
            attrs = op.get("attributes", {}) or {}
            # Explicit task mention
            if isinstance(insert, dict) and "task_mention" in insert:
                mention = insert["task_mention"]
                tid = mention.get("task_id")
                if tid:
                    cid = mention.get("custom_id") or tid
                    nm = mention.get("name") or ""
                    task_lookup[tid] = (cid, nm or task_lookup.get(tid, (cid, ""))[1])
                    task_lookup[cid] = (cid, nm or task_lookup.get(cid, (cid, ""))[1])
            # Text with hyperlink to a task (may be /t/<team>/<CUSTOM-ID>)
            if isinstance(insert, str) and "link" in attrs:
                link = attrs["link"]
                m = TASK_ANY_URL_RE.match(link)
                if m:
                    key = m.group(1)
                    visible_text = insert.strip()
                    if visible_text:
                        cid, nm = task_lookup.get(key, (key, ""))
                        # Use visible text as name hint if we don't have one
                        if not nm:
                            task_lookup[key] = (cid, visible_text)

def render_quill_ops(ops, task_lookup, make_button, styles):
    flows = []
    text_buffer = ""

    def flush_buffer():
        nonlocal text_buffer
        if text_buffer.strip():
            html = urlify_text(text_buffer, task_lookup)
            flows.append(Paragraph(html.replace('\n', '<br/>'), styles['NormalText']))
        text_buffer = ""

    for op in ops:
        insert = op.get("insert")
        attrs = op.get("attributes", {}) or {}

        # 1) Task mention → button
        if isinstance(insert, dict) and "task_mention" in insert:
            flush_buffer()
            mention = insert["task_mention"]
            task_id = mention.get("task_id", "")
            cid = mention.get("custom_id") or task_id
            name = mention.get("name") or task_lookup.get(task_id, (cid, ""))[1]
            url = f"https://app.clickup.com/t/{task_id}"
            flows.append(make_button(f"[{cid}] {name or 'ClickUp Task'}", url))
            flows.append(Spacer(1, 4))
            # Keep both keys mapped
            task_lookup[task_id] = (cid, name or task_lookup.get(task_id, (cid, ""))[1])
            task_lookup[cid] = (cid, name or task_lookup.get(cid, (cid, ""))[1])
            continue

        # 2) Inline image
        if isinstance(insert, dict) and "image" in insert:
            flush_buffer()
            img_url = insert["image"]
            try:
                flows.append(Image(img_url, width=2*inch, height=2*inch))
            except Exception:
                flows.append(Paragraph(f"[Image: {img_url}]", styles['NormalText']))
            continue

        # 3) Plain string (may be formatted or a hyperlink)
        if isinstance(insert, str):
            # Hyperlink case
            if "link" in attrs:
                link = attrs["link"]
                m = TASK_ANY_URL_RE.match(link)
                if m:
                    flush_buffer()
                    key = m.group(1)
                    cid, nm = task_lookup.get(key, (key, ""))
                    label = f"[{cid}] {nm or insert.strip() or 'ClickUp Task'}"
                    flows.append(make_button(label, link))
                    flows.append(Spacer(1, 4))
                    # keep lookup fresh
                    if key not in task_lookup or not task_lookup[key][1]:
                        task_lookup[key] = (cid, nm or insert.strip())
                    continue
            # Code block line → use CodeBlock style
            if "code-block" in attrs:
                flush_buffer()
                flows.append(Paragraph(insert.replace('\n', '<br/>'), styles['CodeBlock']))
                continue
            # Bold/italic are inline; we keep simple and aggregate, Quill ops already split them
            if attrs.get("bold"):
                text_buffer += f"<b>{insert}</b>"
            elif attrs.get("italic"):
                text_buffer += f"<i>{insert}</i>"
            else:
                text_buffer += insert

    flush_buffer()
    return flows
