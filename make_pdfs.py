#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
from pathlib import Path
from typing import Optional, Tuple, List, Dict

from dotenv import load_dotenv
import requests

# PDF bits (reuse your renderer)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate
from renderers import build_story

# --------------------------------------------------------------------------------------
# Parsing & API helpers
# --------------------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://(?:app\.)?clickup\.com/t(?:/(\d+))?/([^/?#]+)", re.I)

def parse_identifier(s: str) -> Tuple[Optional[str], str]:
    """
    Accepts:
      - URL: https://app.clickup.com/t/<team>/<CUSTOM_ID> or https://app.clickup.com/t/<CUSTOM_ID>
      - Custom ID: e.g., PERSON-20340
      - Numeric task ID: e.g., 9012345678
    Returns: (team_id_or_None, task_key)
    """
    s = s.strip()
    m = _URL_RE.match(s)
    if m:
        return (m.group(1), m.group(2))
    return (None, s)

def is_custom_id(task_key: str) -> bool:
    # Pure digits => task_id, else assume custom_id
    return not task_key.isdigit()

def ensure_api_key(cli_key: Optional[str]) -> str:
    api = cli_key or os.getenv("CLICKUP_API_KEY")
    if not api:
        raise SystemExit("Missing API key. Provide --api-key or set CLICKUP_API_KEY in .env")
    return api

def resolve_team_id(url_team: Optional[str], cli_team: Optional[str]) -> Optional[str]:
    """
    Priority: URL > --team > CLICKUP_TEAM_ID (from .env)
    """
    return url_team or cli_team or os.getenv("CLICKUP_TEAM_ID")

def fetch_task(task_key: str, team_id: Optional[str], api_key: str, include_md: bool = True) -> Dict:
    """
    Fetch task JSON from ClickUp.
    - If task_key is custom ID -> requires team_id (unless embedded in URL or in env).
    - If task_key is numeric -> team_id ignored.
    """
    headers = {"Authorization": api_key}
    params = {}
    if is_custom_id(task_key):
        if not team_id:
            raise SystemExit(
                "Custom ID requires a team id. Provide --team, set CLICKUP_TEAM_ID in .env, "
                "or use a URL containing /t/<team>/<CUSTOM-ID>."
            )
        params["custom_task_ids"] = "true"
        params["team_id"] = str(team_id)

    if include_md:
        params["include_markdown_description"] = "true"

    url = f"https://api.clickup.com/api/v2/task/{task_key}"
    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch task {task_key}. HTTP {r.status_code} - {r.text}")
    return r.json()

# --------------------------------------------------------------------------------------
# Naming, sequencing, and I/O
# --------------------------------------------------------------------------------------

NAME_RE = re.compile(r"^(\d{4})\s*-\s*(.+)\.(json|pdf)$", re.I)

def next_sequence(outputs_dir: Path) -> int:
    """
    Scan outputs_dir for files named like '0007 - something.json/pdf'
    and return the next sequence integer.
    """
    max_seq = 0
    if outputs_dir.exists():
        for p in outputs_dir.iterdir():
            m = NAME_RE.match(p.name)
            if m:
                try:
                    max_seq = max(max_seq, int(m.group(1)))
                except ValueError:
                    pass
    return max_seq + 1

def sanitize_basename(s: str) -> str:
    # collapse whitespace and non-filename chars
    s = re.sub(r"[^\w\-]+", "_", s, flags=re.U).strip("_")
    s = re.sub(r"_+", "_", s)
    return s[:120] if s else "task"

def choose_stem(task_key: str, task: Dict) -> str:
    """
    Build a useful stem: <task_key>__<short_title>
    """
    title = (task.get("name") or "").strip()
    short = title[:60]
    stem = f"{task_key}__{short}" if short else task_key
    return sanitize_basename(stem)

def render_pdf(task: Dict, pdf_path: Path):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm, bottomMargin=16*mm,
        title=task.get('name') or 'ClickUp PDF',
        author="clickup-pdf-generator",
    )
    story = build_story(task)
    doc.build(story)

# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def main():
    # Load .env up-front so both API key and CLICKUP_TEAM_ID are available
    load_dotenv()

    ap = argparse.ArgumentParser(
        description="Fetch one or more ClickUp tasks and emit paired JSON/PDF files into ./outputs with persistent sequencing."
    )
    ap.add_argument(
        "identifiers", nargs="+",
        help="One or more task URLs, custom IDs (e.g. PERSON-20340), or numeric task IDs."
    )
    ap.add_argument(
        "--team", help="Team ID (optional if using URL or CLICKUP_TEAM_ID is set in .env)."
    )
    ap.add_argument(
        "--outputs", default="outputs",
        help="Output directory (default: outputs)"
    )
    ap.add_argument(
        "--api-key", dest="api_key", default=None,
        help="Override CLICKUP_API_KEY from environment/.env"
    )
    ap.add_argument(
        "--no-markdown", action="store_true",
        help="Do NOT include markdown_description"
    )
    args = ap.parse_args()

    api_key = ensure_api_key(args.api_key)
    outdir = Path(args.outputs).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    seq = next_sequence(outdir)

    results: List[Tuple[str, Path, Path]] = []
    errors: List[str] = []

    for raw in args.identifiers:
        try:
            url_team, key = parse_identifier(raw)
            team_id = resolve_team_id(url_team, args.team)

            task = fetch_task(key, team_id, api_key, include_md=(not args.no_markdown))

            # Stem and paths
            stem = choose_stem(key, task)
            base = f"{seq:04d} - {stem}"
            json_path = outdir / f"{base}.json"
            pdf_path  = outdir / f"{base}.pdf"

            # Write JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(task, f, indent=2)

            # Render PDF
            render_pdf(task, pdf_path)

            results.append((key, json_path, pdf_path))
            seq += 1
        except Exception as e:
            errors.append(f"{raw} -> {e}")

    # Report
    if results:
        print("✅ Created the following files:")
        for key, jp, pp in results:
            print(f"  - {jp.name}")
            print(f"  - {pp.name}")
        print(f"\n📂 Directory: {outdir}")

    if errors:
        print("\n⚠️ Some items failed:")
        for line in errors:
            print(f"  - {line}")

if __name__ == "__main__":
    main()
