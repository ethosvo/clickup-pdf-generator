#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://(?:app\.)?clickup\.com/t(?:/(\d+))?/([^/?#]+)", re.I)

def parse_identifier(s: str):
    """
    Accepts either:
      - Full URL: https://app.clickup.com/t/<team_id>/<CUSTOM_ID>
                  https://app.clickup.com/t/<CUSTOM_ID>
      - Custom ID or Task ID directly: e.g. PERSON-20340 or 9012345678
    Returns: (team_id_or_None, task_key)
    """
    m = _URL_RE.match(s.strip())
    if m:
        team = m.group(1)
        key  = m.group(2)
        return (team, key)
    return (None, s.strip())

def is_custom_id(task_key: str) -> bool:
    """
    Heuristic: ClickUp custom IDs usually contain letters or a dash.
    Pure digits => likely the real task_id.
    """
    return not task_key.isdigit()

def ensure_api_key(cli_key: str | None) -> str:
    load_dotenv()
    api = cli_key or os.getenv("CLICKUP_API_KEY")
    if not api:
        raise ValueError("Missing API key. Provide via --api-key or CLICKUP_API_KEY in .env")
    return api

# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Fetch a ClickUp task and save JSON locally (supports custom IDs)."
    )
    ap.add_argument(
        "identifier",
        help="Task URL (https://app.clickup.com/t/<team>/<CUSTOM-ID>) "
             "or custom ID (e.g. PERSON-20340) or real task ID (digits)."
    )
    ap.add_argument(
        "--team",
        help="Team ID (required when using custom IDs unless present in URL)."
    )
    ap.add_argument(
        "--out", default="task_data.json",
        help="Output JSON file (default: task_data.json)"
    )
    ap.add_argument(
        "--api-key", dest="api_key", default=None,
        help="Override CLICKUP_API_KEY from environment/.env"
    )
    ap.add_argument(
        "--no-markdown", action="store_true",
        help="Do NOT ask ClickUp to include markdown_description"
    )
    args = ap.parse_args()

    api_key = ensure_api_key(args.api_key)

    # Parse identifier
    url_team, key = parse_identifier(args.identifier)
    team_id = url_team or args.team

    use_custom = is_custom_id(key)
    if use_custom and not team_id:
        raise SystemExit(
            "When using a custom task ID (e.g. PERSON-20340), a team ID is required.\n"
            "Supply it via --team or include it in the URL (…/t/<team>/<CUSTOM-ID>)."
        )

    headers = {"Authorization": api_key}
    endpoint = f"https://api.clickup.com/api/v2/task/{key}"

    params = {}
    if use_custom:
        params["custom_task_ids"] = "true"
        params["team_id"] = str(team_id)

    if not args.no_markdown:
        params["include_markdown_description"] = "true"

    resp = requests.get(endpoint, headers=headers, params=params, timeout=30)
    if resp.status_code != 200:
        raise SystemExit(
            f"Failed to fetch task.\nHTTP: {resp.status_code}\nBody: {resp.text}"
        )

    task = resp.json()

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2)

    # Friendly summary
    name = task.get("name") or "(no name)"
    print("✅ Fetched task")
    if team_id:
        print(f"   team_id: {team_id}")
    print(f"   key/id : {key}")
    print(f"   title  : {name}")
    print(f"💾 Saved  : {args.out}")

if __name__ == "__main__":
    main()
