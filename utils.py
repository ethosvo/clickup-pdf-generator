# utils.py
import re

def esc(s: str) -> str:
    """Escape for ReportLab Paragraph (mini HTML subset)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def coalesce_list_attr(list_attr):
    """ClickUp sometimes exports {"list": "bullet"}; normalize to 'bullet'."""
    if isinstance(list_attr, dict):
        return list_attr.get('list')
    return list_attr

# --- Minimal Markdown fallback for plain text fields ---
_bold_re = re.compile(r"\*\*(.+?)\*\*")          # **bold**
_link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)") # [text](url)

def md_inline_to_html(s: str) -> str:
    """
    Convert a tiny subset of Markdown to the HTML subset ReportLab understands.
    - **bold** -> <b>…</b>
    - [text](url) -> <a href="url">text</a>
    Escape everything else first.
    """
    if not s:
        return ""
    t = esc(s)
    # links first so inner **bold** in link text is handled next
    t = _link_re.sub(lambda m: f'<a href="{esc(m.group(2))}">{esc(m.group(1))}</a>', t)
    t = _bold_re.sub(lambda m: f"<b>{esc(m.group(1))}</b>", t)
    return t
