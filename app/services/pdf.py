import os
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from bs4 import BeautifulSoup
from app.core.config import settings

logger = logging.getLogger("app.services.pdf")

GOLD = HexColor("#D4AF37")
DARK_BG = HexColor("#1A1A2E")
DARK_GRAY = HexColor("#333333")

def generate_pdf_from_html(html_content: str, output_filename: str) -> str:
    """Renders HTML content to PDF using ReportLab (pure Python, Vercel-compatible)."""
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(settings.PDF_OUTPUT_DIR, output_filename)

    soup = BeautifulSoup(html_content, 'html.parser')
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm,
        title="Rian Studioz Quotation")
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=24, textColor=DARK_BG, alignment=TA_CENTER, spaceAfter=2*mm, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=12, textColor=GOLD, alignment=TA_CENTER, spaceAfter=6*mm, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('H2', parent=styles['Heading2'],
        fontSize=16, textColor=GOLD, spaceBefore=8*mm, spaceAfter=4*mm, fontName='Helvetica-Bold')
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, textColor=DARK_GRAY, leading=14)
    total_style = ParagraphStyle('Total', parent=styles['Normal'],
        fontSize=14, textColor=DARK_BG, alignment=TA_RIGHT, fontName='Helvetica-Bold')

    t = soup.find('h1', class_='quote-brand-name')
    s = soup.find('p', class_='quote-brand-tagline')
    story.append(Paragraph(t.get_text(strip=True) if t else "Rian Studioz", title_style))
    if s: story.append(Paragraph(s.get_text(strip=True), subtitle_style))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD))
    story.append(Spacer(1, 4*mm))

    qi = soup.find('div', class_='quote-info-grid')
    if qi:
        for item in qi.find_all('div', class_='info-item'):
            l = item.find('span', class_='label')
            v = item.find('span', class_='value')
            if l and v: story.append(Paragraph(f"<b>{l.get_text(strip=True)}:</b> {v.get_text(strip=True)}", normal))
        story.append(Spacer(1, 4*mm))

    intro = soup.find('div', class_='quote-intro')
    if intro:
        story.append(Paragraph(intro.get_text(strip=True).replace('\n', '<br/>'), normal))
        story.append(Spacer(1, 4*mm))

    for sdiv in soup.find_all('div', class_='package-section'):
        h = sdiv.find(['h2', 'h3'], class_='section-title')
        if h: story.append(Paragraph(h.get_text(strip=True), heading_style))
        tdata = [['Description', 'Qty', 'Rate (₹)', 'Total (₹)']]
        for row in sdiv.find_all('tr', class_='item-row'):
            cells = row.find_all('td')
            if len(cells) >= 4: tdata.append([cells[i].get_text(strip=True) for i in range(4)])
        if len(tdata) > 1:
            tbl = Table(tdata, colWidths=[70*mm, 15*mm, 30*mm, 30*mm])
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), GOLD), ('TEXTCOLOR', (0,0), (-1,0), black),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 9),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 0.5, HexColor('#DDD')),
                ('FONTSIZE', (0,1), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 3*mm))

    for d in soup.find_all('div', class_='deliverable-item'):
        desc = d.find('span', class_='description')
        comp = d.find('span', class_='complimentary-badge')
        txt = desc.get_text(strip=True) if desc else ""
        if comp: txt += " ★ Complimentary"
        story.append(Paragraph(f"• {txt}", normal))

    ts = soup.find('div', class_='totals-section')
    if ts:
        story.append(Spacer(1, 3*mm))
        for line in ts.find_all('div', class_='total-line'):
            l = line.find('span', class_='label'); v = line.find('span', class_='value')
            if l and v:
                is_last = 'grand' in l.get_text(strip=True).lower() or 'total' in l.get_text(strip=True).lower()
                sty = total_style if is_last else normal
                story.append(Paragraph(f"<b>{l.get_text(strip=True)}:</b> {v.get_text(strip=True)}", sty))

    pays = soup.find_all('div', class_='payment-split-item')
    if pays:
        story.append(Spacer(1, 5*mm))
        story.append(Paragraph("Payment Schedule", heading_style))
        for p in pays:
            stg = p.find('span', class_='stage'); amt = p.find('span', class_='amount')
            if stg and amt: story.append(Paragraph(f"• {stg.get_text(strip=True)}: {amt.get_text(strip=True)}", normal))

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD))
    story.append(Spacer(1, 2*mm))
    ft = soup.find('div', class_='quote-footer')
    if ft:
        story.append(Paragraph(ft.get_text(strip=True).replace('\n', '<br/>'),
            ParagraphStyle('Foot', parent=normal, fontSize=8, alignment=TA_CENTER)))

    doc.build(story)
    logger.info(f"PDF generated: {output_filename}")
    return f"/static/pdfs/{output_filename}"
