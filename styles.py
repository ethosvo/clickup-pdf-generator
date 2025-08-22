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
    return styles
