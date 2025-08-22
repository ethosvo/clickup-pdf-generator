from reportlab.platypus import Paragraph, Spacer, KeepInFrame
from clickup_parser import render_quill_ops
from utils import urlify_text

def resolve_id(obj: dict) -> str:
    return obj.get("custom_id") or obj.get("id", "")

def make_button(label: str, url: str, styles):
    p = Paragraph(f"<a href='{url}'>{label}</a>", styles['ButtonLink'])
    return KeepInFrame(maxWidth=200, maxHeight=40,
                       content=[p], hAlign='LEFT', mode='shrink')

def format_people(people_list, styles):
    flows = []
    for person in people_list or []:
        name = person.get("name", "").strip()
        url = person.get("url", "").strip()
        tid = resolve_id(person)
        if not name:
            continue
        if url and tid:
            flows.append(make_button(f"[{tid}] {name}", url, styles))
        elif url:
            flows.append(make_button(name, url, styles))
        else:
            flows.append(Paragraph(name, styles['NormalText']))
        flows.append(Spacer(1, 4))
    return flows

def render_value(field_value, rich_text_ops, task_lookup, styles):
    flows = []
    if isinstance(rich_text_ops, str):
        try:
            import json
            ops = json.loads(rich_text_ops).get("ops", [])
            flows.extend(render_quill_ops(ops, task_lookup, lambda l,u: make_button(l,u,styles), styles))
            return flows
        except Exception:
            pass

    if isinstance(field_value, list) and field_value and isinstance(field_value[0], dict) and "name" in field_value[0]:
        flows.extend(format_people(field_value, styles))
        return flows

    if isinstance(field_value, dict) and "name" in field_value:
        name = field_value.get("name", "")
        url = field_value.get("url", "")
        tid = resolve_id(field_value)
        if url and tid:
            flows.append(make_button(f"[{tid}] {name}", url, styles))
        elif url:
            flows.append(make_button(name, url, styles))
        else:
            flows.append(Paragraph(name, styles['NormalText']))
        flows.append(Spacer(1, 4))
        return flows

    if isinstance(field_value, str):
        flows.append(Paragraph(urlify_text(field_value.strip(), task_lookup), styles['NormalText']))
        return flows

    flows.append(Paragraph(str(field_value), styles['NormalText']))
    return flows
