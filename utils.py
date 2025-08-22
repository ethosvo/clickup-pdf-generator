import re

URL_RE = re.compile(r'(https?://\S+)', re.IGNORECASE)
TASK_URL_RE = re.compile(r'https://app\.clickup\.com/t/([a-zA-Z0-9]+)')
TASK_BRACKET_RE = re.compile(r'\[([a-zA-Z0-9]+)\]\s*ClickUp Task')

def safe_filename(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    return name or "Untitled"

def urlify_text(text: str, task_lookup: dict) -> str:
    def repl_url(match):
        url = match.group(1).rstrip(').,;')
        m = TASK_URL_RE.match(url)
        if m:
            tid = m.group(1)
            custom_id, name = task_lookup.get(tid, (tid, "ClickUp Task"))
            label = f"[{custom_id}] {name}" if name else f"[{custom_id}] ClickUp Task"
            return f"<a href='{url}'>{label}</a>"
        return f"<a href='{url}'>{url}</a>"
    return URL_RE.sub(repl_url, text or '')
