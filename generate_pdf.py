# generate_pdf.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate
from renderers import build_story

def main():
    ap = argparse.ArgumentParser(description="Generate formatted PDF from ClickUp JSON.")
    ap.add_argument('--in', dest='infile', default='task_data.json', help='Path to task JSON')
    ap.add_argument('--out', dest='outfile', default='output.pdf', help='Output PDF path')
    args = ap.parse_args()

    in_path, out_path = Path(args.infile), Path(args.outfile)
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    with in_path.open('r', encoding='utf-8') as f:
        task = json.load(f)

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm, bottomMargin=16*mm,
        title=task.get('name') or 'ClickUp PDF',
        author="clickup-pdf-generator",
    )
    story = build_story(task)
    doc.build(story)
    print(f"PDF written to: {out_path}")

if __name__ == '__main__':
    main()
