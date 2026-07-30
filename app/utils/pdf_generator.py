import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_invoice_pdf(order_data, filepath):
    """
    Generates a professional PDF invoice using ReportLab with Indian Rupees (₹).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    company_info = "<b>INVENTORY & STOCK SYSTEM</b><br/>123 Innovation Drive, Tech City<br/>Email: support@inventorysystem.com<br/>Phone: +91 98765 43210"
    invoice_meta = f"<b>INVOICE</b><br/>Invoice #: {order_data.get('invoice_number')}<br/>Date: {order_data.get('created_at')}<br/>Status: <font color='#16a34a'><b>{order_data.get('status')}</b></font>"

    header_table_data = [
        [Paragraph(company_info, styles['Normal']), Paragraph(invoice_meta, ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=2))]
    ]
    
    header_table = Table(header_table_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#e2e8f0"), spaceAfter=15))

    # Customer info
    cust_info = f"<b>Billed To:</b><br/><b>{order_data.get('customer_name', 'Customer')}</b><br/>Email: {order_data.get('customer_email', 'N/A')}"
    story.append(Paragraph(cust_info, styles['Normal']))
    story.append(Spacer(1, 15))

    # Line Items Table
    table_data = [
        [Paragraph("<b>Item / SKU</b>", styles['Normal']),
         Paragraph("<b>Unit Price</b>", styles['Normal']),
         Paragraph("<b>Qty</b>", styles['Normal']),
         Paragraph("<b>Subtotal</b>", styles['Normal'])]
    ]

    for item in order_data.get('items', []):
        item_title = f"<b>{item.get('product_name')}</b><br/><font color='#64748b' size=8>SKU: {item.get('product_sku')}</font>"
        table_data.append([
            Paragraph(item_title, styles['Normal']),
            f"₹{item.get('unit_price'):,.2f}",
            str(item.get('quantity')),
            f"₹{item.get('subtotal'):,.2f}"
        ])

    table = Table(table_data, colWidths=[270, 90, 60, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))

    # Totals Summary Table
    summary_data = [
        ["Subtotal:", f"₹{order_data.get('subtotal', 0):,.2f}"],
        ["Tax:", f"₹{order_data.get('tax_amount', 0):,.2f}"],
        ["Discount:", f"-₹{order_data.get('discount_amount', 0):,.2f}"],
        ["Total Amount:", f"₹{order_data.get('total_amount', 0):,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[420, 120])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 12),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor("#0f172a")),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(summary_table)

    story.append(Spacer(1, 30))
    footer_text = "<font color='#94a3b8' size=9>Thank you for your business! If you have any questions about this invoice, please contact support.</font>"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=1)))

    doc.build(story)
    return filepath
