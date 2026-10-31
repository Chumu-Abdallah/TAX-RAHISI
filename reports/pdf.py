from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.utils import timezone

def generate_tax_summary_pdf(business, data, tax_year):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph(f"<b>TAX-RAHISI - Muhtasari wa Kodi</b>", styles['Heading']))
    story.append(Paragraph(f"Biashara: {business.business_name} | TIN: {business.tin}", styles['Normal']))
    story.append(Paragraph(f"Mwaka wa kodi: {tax_year} | Tarehe: {timezone.now().date()}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Table ya hesabu
    table_data = [
        ['Maelezo', 'Kiasi (TZS)'],
        ['Jumla ya Mauzo', f"{data['sales_total']:,.2f}"],
        ['Jula ya Matumizu', f"{data['expenses_total']:,.2f}"],
        ['Faida (profit)', f"{data['profit']:,.2f}"],
        ['Kodi inayodaiwa', f"{data['tax_payable']:.2f}"],
        ['Kodi Iliolipwa', f"{data['tax_paid']:,.2f}"],
        ['Baki', f"{data['tax_balance']:,.2f}"],
    ]
    table = Table(table_data, colWidths=[250, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HaxColor('#0F172A')),
        ('TEXTCOLOR', (0.0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.beig),
    ]))
    story.append(table)
    story.append(Spacer(1, 30))
    story.append(Paragraph("Hii ni ripoti ya mchanganuo tu, si risiti rasmin ya TRA.", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_profit_loss_pdf(business, sales_qs, expenses_qs):
    # Similar logic - unaweza kutumia function ya juu
    pass