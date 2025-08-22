from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, leading=18,
                              spaceAfter=6, spaceBefore=12,
                              textColor=colors.darkblue, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='NormalText', fontSize=10, leading=14,
                              alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='ButtonLink',
                              fontSize=9, leading=11,
                              textColor=colors.black,
                              backColor=colors.whitesmoke,
                              borderColor=colors.grey,
                              borderWidth=0.5,
                              borderRadius=6,
                              borderPadding=(2, 6, 2, 6),
                              spaceAfter=4, spaceBefore=2,
                              alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='CodeBlock',
                              fontName='Courier',
                              fontSize=9, leading=12,
                              textColor=colors.black,
                              backColor=colors.HexColor('#f5f5f5'),
                              borderColor=colors.HexColor('#dddddd'),
                              borderWidth=0.5,
                              borderPadding=(6, 8, 6, 8),
                              spaceAfter=6, spaceBefore=4))
    return styles
