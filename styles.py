# styles.py
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

BLUE = "#1f6feb"  # pleasant blue
RED = "#c62828"   # warning red

def build_styles():
    ss = getSampleStyleSheet()

    body = ParagraphStyle(
        'Body', parent=ss['BodyText'],
        fontName='Helvetica', fontSize=10.5, leading=14, spaceAfter=4,
    )
    h1 = ParagraphStyle(
        'H1', parent=ss['Heading1'],
        fontName='Helvetica-Bold', fontSize=20, leading=24,
        textColor=BLUE, spaceBefore=10, spaceAfter=6,
    )
    h2 = ParagraphStyle(
        'H2', parent=ss['Heading2'],
        fontName='Helvetica-Bold', fontSize=16, leading=20,
        textColor=BLUE, spaceBefore=10, spaceAfter=4,
    )
    h3 = ParagraphStyle(
        'H3', parent=ss['Heading3'],
        fontName='Helvetica-Bold', fontSize=13, leading=17,
        textColor=BLUE, spaceBefore=8, spaceAfter=3,
    )
    meta = ParagraphStyle(
        'Meta', parent=body, fontSize=9, leading=12,
        textColor="#555555", spaceAfter=2,
    )
    link = ParagraphStyle('Link', parent=meta, textColor=BLUE)
    warn = ParagraphStyle(
        'Warn', parent=body, textColor=RED,
        fontName='Helvetica-Oblique', spaceAfter=3,
    )
    return {'body': body, 'h1': h1, 'h2': h2, 'h3': h3, 'meta': meta, 'link': link, 'warn': warn}
