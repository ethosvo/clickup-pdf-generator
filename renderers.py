# renderers.py
import json
from typing import Any, Dict, List

from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch

from styles import build_styles
from utils import esc, coalesce_list_attr, md_inline_to_html

def _wrap_inline(text: str, attrs: Dict[str, Any]) -> str:
    """Apply inline formatting supported by ReportLab (<b>, <i>, <a>)."""
    t = esc(text)
    link = attrs.get('link')
    bold = bool(attrs.get('bold'))
    italic = bool(attrs.get('italic'))
    if bold:
        t = f"<b>{t}</b>"
    if italic:
        t = f"<i>{t}</i>"
    if link:
        href = esc(str(link))
        t = f'<a href="{href}">{t}</a>'
    return t

def quill_to_flowables(delta_ops: List[Dict[str, Any]], styles) -> List[Any]:
    """Convert Quill Delta to flowables (handles attrs on newline)."""
    flow: List[Any] = []
    line_buf = ""
    bullet_buf: List[str] = []

    def flush_bullets():
        nonlocal bullet_buf
        if bullet_buf:
            items = [ListItem(Paragraph(x, styles['body'])) for x in bullet_buf]
            flow.append(ListFlowable(items, bulletType='bullet', start='•', leftIndent=16))
            bullet_buf = []

    def emit_block(text: str, attrs: Dict[str, Any]):
        header = attrs.get('header')
        list_attr = coalesce_list_attr(attrs.get('list'))
        if list_attr == 'bullet':
            if text.strip():
                bullet_buf.append(text.strip())
            return
        flush_bullets()
        text = text.strip()
        if not text:
            flow.append(Spacer(1, 2)); return
        if header == 1:
            flow.append(Paragraph(text, styles['h1']))
        elif header == 2:
            flow.append(Paragraph(text, styles['h2']))
        elif header == 3:
            flow.append(Paragraph(text, styles['h3']))
        else:
            flow.append(Paragraph(text, styles['body']))

    for op in delta_ops:
        ins = op.get('insert', '')
        attrs = op.get('attributes', {}) or {}
        if isinstance(ins, str) and ins != '\n':
            if '\n' in ins:
                parts = ins.split('\n')
                for part in parts[:-1]:
                    line_buf += _wrap_inline(part, attrs)
                    emit_block(line_buf, {})
                    line_buf = ""
                line_buf += _wrap_inline(parts[-1], attrs)
            else:
                line_buf += _wrap_inline(ins, attrs)
        elif ins == '\n':
            emit_block(line_buf, attrs); line_buf = ""
        else:
            # (images/mentions could be handled here if needed)
            pass

    if line_buf.strip():
        emit_block(line_buf, {})
    flush_bullets()
    flow.append(Spacer(1, 4))
    return flow

# --- Minimal Markdown (for task.description / task.markdown_description) ---
def _render_markdown(md_text: str, styles) -> List[Any]:
    """
    Very small MD renderer:
      - Headings: #, ##, ###
      - Bullets: lines starting with "- " or "* "
      - Inline: md_inline_to_html() (**bold**, [link](url)); bare text → escaped
      - Blank lines → spacing
    """
    if not md_text:
        return []
    flow: List[Any] = []
    lines = md_text.replace('\r\n', '\n').split('\n')
    bullets: List[str] = []

    def flush_bullets():
        nonlocal bullets
        if not bullets:
            return
        items = [ListItem(Paragraph(md_inline_to_html(x), styles['body'])) for x in bullets]
        flow.append(ListFlowable(items, bulletType='bullet', start='•', leftIndent=16))
        bullets = []

    for raw in lines:
        line = raw.rstrip()

        # headings
        if line.startswith('### '):
            flush_bullets()
            flow.append(Paragraph(md_inline_to_html(line[4:]), styles['h3']))
            continue
        if line.startswith('## '):
            flush_bullets()
            flow.append(Paragraph(md_inline_to_html(line[3:]), styles['h2']))
            continue
        if line.startswith('# '):
            flush_bullets()
            flow.append(Paragraph(md_inline_to_html(line[2:]), styles['h1']))
            continue

        # bullets
        ls = line.lstrip()
        if ls.startswith('- ') or ls.startswith('* '):
            bullets.append(ls[2:].strip())
            continue

        # blank line
        if line.strip() == '':
            flush_bullets()
            flow.append(Spacer(1, 4))
            continue

        # paragraph
        flush_bullets()
        flow.append(Paragraph(md_inline_to_html(line), styles['body']))

    flush_bullets()
    flow.append(Spacer(1, 6))
    return flow

def _render_plain_with_md(story, text: str, styles):
    """
    Fallback renderer for plain text fields that contain lightweight markdown.
    - Preserves blank lines as paragraph breaks.
    - Supports **bold** and [text](url).
    """
    blocks = []
    raw_blocks = text.replace('\r\n', '\n').split('\n\n')
    for blk in raw_blocks:
        lines = [ln for ln in blk.split('\n')]
        if len(lines) == 1:
            blocks.append(lines[0])
        else:
            blocks.extend(lines)
        blocks.append('')
    if blocks and blocks[-1] == '':
        blocks.pop()

    for para in blocks:
        if para.strip():
            story.append(Paragraph(md_inline_to_html(para.strip()), styles['body']))
        else:
            story.append(Spacer(1, 4))
    story.append(Spacer(1, 2))

def add_title_and_meta(story, task, styles):
    title = task.get('name') or 'ClickUp Task'
    url = task.get('url')
    story.append(Paragraph(esc(title), styles['h1']))
    if url:
        story.append(Paragraph(f'<a href="{esc(url)}">{esc(url)}</a>', styles['link']))

    # Owner (if present)
    owner_field = next((f for f in task.get('custom_fields', []) if f.get('name') == 'Owner of this VE'), None)
    if owner_field and isinstance(owner_field.get('value'), list) and owner_field['value']:
        owner = owner_field['value'][0].get('name', '')
        owner_url = owner_field['value'][0].get('url')
        if owner:
            if owner_url:
                story.append(Paragraph(f"<b>Owner:</b> <a href=\"{esc(owner_url)}\">{esc(owner)}</a>", styles['meta']))
            else:
                story.append(Paragraph(f"<b>Owner:</b> {esc(owner)}", styles['meta']))
    story.append(Spacer(1, 8))

def render_url_field(story, field: Dict[str, Any], styles, label: str = None):
    if not field or not field.get('value'):
        return
    url = str(field.get('value'))
    label = label or field.get('name') or 'Link'
    story.append(Paragraph(esc(label), styles['h2']))
    story.append(Paragraph(f'<a href="{esc(url)}">{esc(url)}</a>', styles['link']))
    story.append(Spacer(1, 6))

def render_relationship_field(story, field: Dict[str, Any], styles, level=3):
    name = field.get('name', 'Related')
    hdr_style = styles['h2'] if level == 2 else styles['h3']
    story.append(Paragraph(esc(name), hdr_style))

    vals = field.get('value')
    if isinstance(vals, list) and len(vals) > 0:
        items = []
        for it in vals:
            nm = it.get('name') or it.get('custom_id') or it.get('id')
            url = it.get('url')
            if nm:
                if url:
                    items.append(ListItem(Paragraph(f'<a href="{esc(url)}">{esc(nm)}</a>', styles['body'])))
                else:
                    items.append(ListItem(Paragraph(esc(nm), styles['body'])))
        story.append(ListFlowable(items, bulletType='bullet', start='•', leftIndent=16) if items else Paragraph('—', styles['body']))
    else:
        story.append(Paragraph('not completed – please think about this', styles['warn']))
    story.append(Spacer(1, 6))

def add_field_rich_or_plain(story, field: Dict[str, Any], styles, level=2):
    name = field.get('name', 'Text')
    rich = field.get('value_richtext') or ''
    plain = field.get('value') or ''

    if not rich and not plain:
        return

    hdr_style = styles['h2'] if level == 2 else styles['h3']
    story.append(Paragraph(esc(name), hdr_style)); story.append(Spacer(1, 2))

    if rich:
        try:
            delta = json.loads(rich)
            ops = delta.get('ops', [])
            story.extend(quill_to_flowables(ops, styles))
            return
        except Exception:
            pass

    # Plain fallback with minimal markdown support
    _render_plain_with_md(story, plain, styles)

def build_story(task: Dict[str, Any]):
    styles = build_styles()
    story = []
    add_title_and_meta(story, task, styles)

    # --- Description (prefer markdown_description, fallback to description) ---
    md_desc = task.get('markdown_description') or ''
    plain_desc = task.get('description') or ''
    if md_desc or plain_desc:
        story.append(Paragraph('Description', styles['h2'])); story.append(Spacer(1, 2))
        if md_desc:
            story.extend(_render_markdown(md_desc, styles))
        else:
            _render_plain_with_md(story, plain_desc, styles)

    # Verbatim (Fathom) link if present
    fields = task.get('custom_fields', [])
    by_name = {f.get('name'): f for f in fields}
    render_url_field(story, by_name.get('AI Recording URL'), styles, label='Verbatim recording')

    # Related section (shows red warning if empty)
    story.append(Paragraph('Related', styles['h2'])); story.append(Spacer(1, 2))
    related_order = [
        'Owner of this VE',
        'Contributors to this value exchange',
        'People identified as possible future contributors',
        'Work Navigator',
        'Wellbeing Mentor',
    ]
    for rname in related_order:
        f = by_name.get(rname)
        if f:
            render_relationship_field(story, f, styles, level=3)

    # Main rich/plain text sections
    preferred = [
        'AI Summary',
        'Looking Back (Value Recognition)',
        'What is your mission?',
        'Summary of Next Actions',
        'Comments on VE Collaborators for this period',
        'Comments on VE collaborators for next period',
        'Time and Money',
    ]
    printed = set()
    for name in preferred:
        f = by_name.get(name)
        if f and f.get('type') == 'text':
            add_field_rich_or_plain(story, f, styles, level=2)
            printed.add(name)

    for f in fields:
        if f.get('type') == 'text' and f.get('name') not in printed:
            add_field_rich_or_plain(story, f, styles, level=2)

    return story
