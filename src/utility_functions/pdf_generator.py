#!/usr/bin/env python3
"""
PDF Generator
Generate PDF documents from text, HTML, and data
"""

import json
import logging
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_simple_pdf(title, content, page_size='letter'):
    """
    Create simple PDF from text
    
    Args:
        title: Document title
        content: Text content (can be list of paragraphs)
        page_size: Page size ('letter' or 'A4')
    
    Returns:
        bytes: PDF data
    """
    buffer = io.BytesIO()
    
    # Set page size
    pagesize = A4 if page_size.lower() == 'a4' else letter
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=pagesize,
                          topMargin=0.75*inch, bottomMargin=0.75*inch,
                          leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    body_style = styles['BodyText']
    
    # Add title
    if title:
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3*inch))
    
    # Add content
    if isinstance(content, list):
        for paragraph in content:
            elements.append(Paragraph(str(paragraph), body_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        # Split by newlines
        paragraphs = str(content).split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                elements.append(Paragraph(paragraph, body_style))
                elements.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(elements)
    
    return buffer.getvalue()


def create_table_pdf(title, headers, data, page_size='letter'):
    """
    Create PDF with table
    
    Args:
        title: Document title
        headers: List of column headers
        data: List of rows (each row is a list)
        page_size: Page size
    
    Returns:
        bytes: PDF data
    """
    buffer = io.BytesIO()
    
    # Set page size
    pagesize = A4 if page_size.lower() == 'a4' else letter
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=pagesize,
                          topMargin=0.75*inch, bottomMargin=0.75*inch,
                          leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Add title
    if title:
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3*inch))
    
    # Prepare table data
    table_data = [headers] + data
    
    # Create table
    table = Table(table_data)
    
    # Style table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    return buffer.getvalue()


def create_report_pdf(title, sections, page_size='letter'):
    """
    Create multi-section report PDF
    
    Args:
        title: Document title
        sections: List of dicts with 'heading' and 'content'
        page_size: Page size
    
    Returns:
        bytes: PDF data
    """
    buffer = io.BytesIO()
    
    # Set page size
    pagesize = A4 if page_size.lower() == 'a4' else letter
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=pagesize,
                          topMargin=0.75*inch, bottomMargin=0.75*inch,
                          leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    body_style = styles['BodyText']
    
    # Add title
    if title:
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.5*inch))
    
    # Add sections
    for section in sections:
        # Section heading
        if 'heading' in section:
            elements.append(Paragraph(section['heading'], heading_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Section content
        if 'content' in section:
            content = section['content']
            if isinstance(content, list):
                for item in content:
                    elements.append(Paragraph(str(item), body_style))
                    elements.append(Spacer(1, 0.1*inch))
            else:
                paragraphs = str(content).split('\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        elements.append(Paragraph(paragraph, body_style))
                        elements.append(Spacer(1, 0.1*inch))
        
        # Add spacing between sections
        elements.append(Spacer(1, 0.3*inch))
        
        # Page break if requested
        if section.get('page_break', False):
            elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    
    return buffer.getvalue()


def handle(event, context):
    """
    OpenFaaS handler for PDF generation
    
    Request body for simple PDF:
    {
        "type": "simple",
        "title": "Document Title",
        "content": "Text content or array of paragraphs",
        "page_size": "letter"  # optional: 'letter' or 'A4'
    }
    
    Request body for table PDF:
    {
        "type": "table",
        "title": "Report Title",
        "headers": ["Col1", "Col2", "Col3"],
        "data": [["row1col1", "row1col2", "row1col3"], ...],
        "page_size": "letter"  # optional
    }
    
    Request body for report PDF:
    {
        "type": "report",
        "title": "Report Title",
        "sections": [
            {"heading": "Section 1", "content": "Content...", "page_break": false},
            {"heading": "Section 2", "content": ["Para 1", "Para 2"]}
        ],
        "page_size": "letter"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received PDF generation request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        pdf_type = payload.get('type', 'simple')
        title = payload.get('title', '')
        page_size = payload.get('page_size', 'letter')
        
        if pdf_type == 'simple':
            content = payload.get('content', '')
            if not content:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'content' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Generating simple PDF...")
            pdf_data = create_simple_pdf(title, content, page_size)
        
        elif pdf_type == 'table':
            headers = payload.get('headers', [])
            data = payload.get('data', [])
            
            if not headers or not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'headers' or 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Generating table PDF...")
            pdf_data = create_table_pdf(title, headers, data, page_size)
        
        elif pdf_type == 'report':
            sections = payload.get('sections', [])
            
            if not sections:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'sections' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Generating report PDF...")
            pdf_data = create_report_pdf(title, sections, page_size)
        
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown PDF type: {pdf_type}"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return {
            "statusCode": 200,
            "body": {
                "pdf": pdf_base64,
                "size_bytes": len(pdf_data),
                "page_size": page_size,
                "message": "PDF generated successfully"
            },
            "headers": {"Content-Type": "application/json"}
        }
    
    except Exception as e:
        logger.error(f"Error in PDF generation: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }

