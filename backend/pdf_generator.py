# backend/pdf_generator.py
"""
PDF Report Generation Module:
- Authentic replica of 'بصمات دكاتره.pdf'
- High-resolution Logo + 'إدارة نظم المعلومات والتحول الرقمي' Header Banner
- Distinct Doctor Info Cards (Name, Code, Contract, Department, Job Title)
- Correct Arabic Font Shaping (no double-reversal bugs)
- Exact 9-column RTL layout, stacked headers, authentic peach highlight (#F59D56)
- Footer with 'Created by Eng. Mohamed Marei' and two-pass page numbering
"""

import os
from typing import Dict, Any, List
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

import arabic_reshaper
from bidi.algorithm import get_display


# Register Arabic Fonts from Windows Fonts directory
FONT_PATH = "C:/Windows/Fonts/tahoma.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/tahomabd.ttf"

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('Arabic', FONT_PATH))
if os.path.exists(FONT_BOLD_PATH):
    pdfmetrics.registerFont(TTFont('Arabic-Bold', FONT_BOLD_PATH))


def ar(text: Any) -> str:
    """Helper to reshape and reorder Arabic text for proper RTL display (strictly once)."""
    if text is None:
        return ""
    s = str(text).strip()
    if not s:
        return ""
    if any('\u0600' <= char <= '\u06FF' for char in s):
        return get_display(arabic_reshaper.reshape(s))
    return s


def ar_lines(text: Any) -> str:
    """Helper to reshape multi-line Arabic text line-by-line for clean vertical stacking."""
    if text is None:
        return ""
    lines = str(text).split('\n')
    return '\n'.join(ar(line) for line in lines)


# Authentic colors from 'بصمات دكاتره.pdf'
PEACH_COLOR = colors.HexColor("#F59D56")
HEADER_BG = colors.HexColor("#F2F2F2")
BORDER_COLOR = colors.HexColor("#A6A6A6")

LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "assets", "logo.jpeg"))
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "logo.jpeg"))


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count and footer branding."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Arabic", 8.5)
        self.setFillColor(colors.HexColor("#333333"))

        # Footer Date on Left
        date_str = datetime.now().strftime("%A, %B %d, %Y")
        self.drawString(56, 22, date_str)

        # Center: Eng. Mohamed Marei attribution
        self.drawCentredString(letter[0] / 2, 22, "Created with Eng. Mohamed Marei")

        # Page Number on Right
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 56, 22, page_str)

        self.restoreState()


def generate_doctor_page_elements(doc: Dict[str, Any], styles: Any) -> List[Any]:
    """Generates the flowable elements for a single doctor's report page."""
    elements = []

    # 1. Top Organization Header Banner with Logo
    header_cells = []
    # Left cell: Logo (if available)
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = RLImage(LOGO_PATH, width=38, height=38)
            left_cell = logo_img
        except Exception:
            left_cell = ""
    else:
        left_cell = ""

    # Right cell: Department & Company Titles
    titles_text = ar_lines("شركة الخدمات الطبية - مستشفى الكهرباء\nإدارة نظم المعلومات والتحول الرقمي")
    right_cell = titles_text

    banner_data = [[left_cell, right_cell]]
    banner_table = Table(banner_data, colWidths=[60, 440])
    banner_table.setStyle(TableStyle([
        ('FONT', (1, 0), (1, 0), 'Arabic-Bold', 9.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 4))

    # 2. Doctor Info Header Cards (Row 1 & Row 2)
    emp_code = str(doc.get('emp_code', '')).strip()
    emp_name = doc.get('emp_name', '')
    job_title = doc.get('job_title', '')
    dept = doc.get('department', '')
    contract = doc.get('contract', '')

    # Row 1 Table: 2 Cards with gap in between
    # Left to right in table: [Name Val (205), Name Lbl (80), GAP (15), Code Val (120), Code Lbl (80)] = 500 pt
    row1_data = [
        [
            ar(emp_name),
            ar("اسم الموظف"),
            "",
            emp_code,
            ar("كود الموظف"),
        ]
    ]
    t_row1 = Table(row1_data, colWidths=[205, 80, 15, 120, 80], rowHeights=[24])
    t_row1.setStyle(TableStyle([
        # Card 1: Name
        ('BOX', (0, 0), (1, 0), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (1, 0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (1, 0), (1, 0), HEADER_BG),
        ('FONT', (0, 0), (0, 0), 'Arabic-Bold', 9),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONT', (1, 0), (1, 0), 'Arabic-Bold', 8.5),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        # Card 2: Code
        ('BOX', (3, 0), (4, 0), 0.5, BORDER_COLOR),
        ('INNERGRID', (3, 0), (4, 0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (4, 0), (4, 0), HEADER_BG),
        ('FONT', (3, 0), (3, 0), 'Arabic-Bold', 10),
        ('ALIGN', (3, 0), (3, 0), 'CENTER'),
        ('FONT', (4, 0), (4, 0), 'Arabic-Bold', 8.5),
        ('ALIGN', (4, 0), (4, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_row1)
    elements.append(Spacer(1, 4))

    # Row 2 Table: 3 Cards with gaps in between
    # Left to right in table: [Contract Val (115), Contract Lbl (42), GAP (10), Dept Val (135), Dept Lbl (45), GAP (10), Job Val (100), Job Lbl (43)] = 500 pt
    row2_data = [
        [
            ar(contract),
            ar("العقد"),
            "",
            ar(dept),
            ar("الادارة"),
            "",
            ar(job_title),
            ar("الوظيفة"),
        ]
    ]
    t_row2 = Table(row2_data, colWidths=[115, 42, 10, 135, 45, 10, 100, 43], rowHeights=[24])
    t_row2.setStyle(TableStyle([
        # Card 1: Contract
        ('BOX', (0, 0), (1, 0), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (1, 0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (1, 0), (1, 0), HEADER_BG),
        ('FONT', (0, 0), (0, 0), 'Arabic', 7.5),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONT', (1, 0), (1, 0), 'Arabic-Bold', 8),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        # Card 2: Department
        ('BOX', (3, 0), (4, 0), 0.5, BORDER_COLOR),
        ('INNERGRID', (3, 0), (4, 0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (4, 0), (4, 0), HEADER_BG),
        ('FONT', (3, 0), (3, 0), 'Arabic', 7.5),
        ('ALIGN', (3, 0), (3, 0), 'CENTER'),
        ('FONT', (4, 0), (4, 0), 'Arabic-Bold', 8),
        ('ALIGN', (4, 0), (4, 0), 'CENTER'),
        # Card 3: Job Title
        ('BOX', (6, 0), (7, 0), 0.5, BORDER_COLOR),
        ('INNERGRID', (6, 0), (7, 0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (7, 0), (7, 0), HEADER_BG),
        ('FONT', (6, 0), (6, 0), 'Arabic', 7.5),
        ('ALIGN', (6, 0), (6, 0), 'CENTER'),
        ('FONT', (7, 0), (7, 0), 'Arabic-Bold', 8),
        ('ALIGN', (7, 0), (7, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_row2)
    elements.append(Spacer(1, 8))

    # 3. Monthly Attendance Grid (9 columns, ordered RTL: rightmost is التاريخ)
    table_headers = [
        ar("وقت التأخير"),
        ar_lines("نوع\nالشفت"),
        ar_lines("الوقت اللي قضاه\nالموظف"),
        ar_lines("انصراف شفت\nمسائي"),
        ar_lines("حضور شفت\nمسائي"),
        ar("انصراف"),
        ar("حضور"),
        ar("اليوم"),
        ar("التاريخ"),
    ]

    table_data = [table_headers]
    table_style_commands = [
        ('FONT', (0, 0), (-1, 0), 'Arabic-Bold', 8),
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]

    records = doc.get('records', [])
    for row_idx, r in enumerate(records, start=1):
        row = [
            r.get('deficit_time', '0:00'),
            r.get('shift_type', ''),
            r.get('time_spent', '0:00'),
            r.get('check_out_2', ''),
            r.get('check_in_2', ''),
            r.get('check_out_1', ''),
            r.get('check_in_1', ''),
            ar(r.get('day', '')),
            r.get('date', ''),
        ]
        table_data.append(row)

        table_style_commands.append(('FONT', (0, row_idx), (-1, row_idx), 'Arabic', 8))
        table_style_commands.append(('FONT', (0, row_idx), (0, row_idx), 'Arabic-Bold', 8))
        table_style_commands.append(('FONT', (2, row_idx), (2, row_idx), 'Arabic-Bold', 8))
        table_style_commands.append(('FONT', (5, row_idx), (6, row_idx), 'Arabic-Bold', 8))

        # Highlighting rules:
        # 1. Deficit time > 0 -> Highlight Deficit (Col 0) and Time Spent (Col 2) in Peach
        if r.get('is_deficit'):
            table_style_commands.append(('BACKGROUND', (0, row_idx), (0, row_idx), PEACH_COLOR))
            table_style_commands.append(('BACKGROUND', (2, row_idx), (2, row_idx), PEACH_COLOR))

        # 2. Late arrival -> Highlight Check-in (Col 6) in Peach
        if r.get('is_late_arrival'):
            table_style_commands.append(('BACKGROUND', (6, row_idx), (6, row_idx), PEACH_COLOR))

    col_widths = [46, 42, 72, 58, 58, 56, 56, 46, 66]

    att_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    att_table.setStyle(TableStyle(table_style_commands))

    elements.append(att_table)
    return elements


def generate_pdf_report(data: Dict[str, Any], output_path: str) -> str:
    """
    Builds the complete multi-page PDF document, exactly matching بصمات دكاتره.pdf.
    Each doctor is rendered on an individual page.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc_template = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=56,
        rightMargin=56,
        topMargin=32,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    doctors = data.get('doctors', [])
    for idx, doc in enumerate(doctors):
        page_elements = generate_doctor_page_elements(doc, styles)
        story.extend(page_elements)

        if idx < len(doctors) - 1:
            story.append(PageBreak())

    doc_template.build(story, canvasmaker=NumberedCanvas)
    return output_path

