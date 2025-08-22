import re

# Matches /t/<id> or /t/<team>/<CUSTOM-ID>
TASK_ANY_URL_RE = re.compile(r'https://app\.clickup\.com/t/(?:\d+/)?([A-Za-z0-9-]+)')
URL_RE = re.compile(r'(https?://\S+)', re.IGNORECASE)
TASK_BRACKET_RE = re.compile(r'\[([a-zA-Z0-9]+)\]\s*ClickUp Task')

def safe_filename(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    return name or "Untitled"

def label_for_key(key: str, task_lookup: dict) -> tuple[str, str]:
    """Return (custom_id, name) for either a task id or a custom id."""
    if key in task_lookup:
        return task_lookup[key]
    # If key looks like a custom id but we only have bare id, fallback to key itself
    return (key, task_lookup.get(key, ('', ''))[1] if key in task_lookup else '')

def urlify_text(text: str, task_lookup: dict, seen_ids: set | None = None) -> str:
    """Convert bare URLs to anchors, using lookup for ClickUp task labels."""
    if seen_ids is None:
        seen_ids = set()

    def repl_url(match):
        url = match.group(1).rstrip(').,;')
        m = TASK_ANY_URL_RE.match(url)
        if m:
            key = m.group(1)  # could be task id or custom id
            custom_id, name = label_for_key(key, task_lookup)
            label = f"[{custom_id}] {name}" if name else f"[{custom_id}] ClickUp Task"
            seen_ids.add(key)
            return f"<a href='{url}'>{label}</a>"
        return f"<a href='{url}'>{url}</a>"

    return URL_RE.sub(repl_url, text or '')
