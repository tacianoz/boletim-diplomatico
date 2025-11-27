"""
PDF Generator for Notas do Dia - India
Modern, clean design with professional layout
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import List, Dict
from app.logger import logger
from app.font_manager import get_appropriate_font
import re
import os


class PDFGenerator:
    """Modern PDF generator for Notas do Dia"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup all paragraph styles for modern design"""
        # Header style - elegant and subtle
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=8,
            alignment=TA_RIGHT,
            textColor=HexColor('#1C2443'),  # Azul escuro para textos gerais
            fontName='Helvetica'
        )
        
        # Main title - smaller and elegant
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=4,
            spaceBefore=0,
            alignment=TA_CENTER,
            textColor=HexColor('#22A749'),  # Verde para "Notas do Dia"
            fontName='Helvetica-Bold',
            leading=22
        )
        
        # Subtitle - date
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,  # Reduzido de 12 para 6
            alignment=TA_CENTER,
            textColor=HexColor('#1C2443'),  # Azul escuro para textos gerais
            fontName='Helvetica'
        )
        
        # Section headers - modern with subtle background
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,  # Reduzido de 24 para 12 (mais compacto)
            textColor=HexColor('#1C2443'),  # Azul escuro para títulos de seção
            fontName='Helvetica-Bold',
            leading=18,
            backColor=HexColor('#FFFFFF'),  # Fundo branco
            borderPadding=8,
            borderWidth=0,
            leftIndent=0
        )
        
        # Document title/link - clean and clickable
        self.link_style = ParagraphStyle(
            'Link',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leading=16,
            textColor=HexColor('#2563eb'),  # Azul claro para links
            fontName='Helvetica',
            alignment=TA_LEFT
        )
        
        # Summary text - readable and clean
        self.summary_style = ParagraphStyle(
            'Summary',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=16,
            leading=15,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#1C2443'),  # Azul escuro para textos gerais
            fontName='Helvetica',
            leftIndent=20,
            rightIndent=20
        )
        
        # Empty section message
        self.empty_style = ParagraphStyle(
            'Empty',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leading=14,
            alignment=TA_CENTER,
            fontStyle='italic',
            textColor=HexColor('#1C2443'),  # Azul escuro para textos gerais
            fontName='Helvetica'
        )
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add elegant header and footer to each page"""
        canvas_obj.saveState()
        
        # Footer - page number and date (removed header line)
        page_num = canvas_obj.getPageNumber()
        footer_text = f"Notas do Dia - India | Página {page_num}"
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(HexColor('#1C2443'))  # Azul escuro para textos gerais
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin,
            doc.bottomMargin - 15,
            footer_text
        )
        
        canvas_obj.restoreState()
    
    def _add_background(self, canvas_obj, doc):
        """Add background color - white"""
        canvas_obj.saveState()
        canvas_obj.setFillColor(HexColor('#FFFFFF'))  # Fundo branco
        canvas_obj.rect(0, 0, 
                      doc.width + doc.leftMargin + doc.rightMargin,
                      doc.height + doc.topMargin + doc.bottomMargin,
                      fill=1)
        canvas_obj.restoreState()
    
    def generate(self, docs: List[Dict], report_text: str, output_filename: str = None) -> str:
        """
        Generate PDF from documents and report text
        
        Args:
            docs: List of document dictionaries
            report_text: Compiled report text from summarizer
            output_filename: Optional custom filename
            
        Returns:
            Path to generated PDF file
        """
        logger.info("=== GERANDO PDF DO NOTAS DO DIA ===")
        
        try:
            # Generate filename
            if not output_filename:
                today = datetime.now().date()
                output_filename = f"notas_do_dia_{today.strftime('%Y%m%d')}.pdf"
            
            # Create document with modern margins
            doc = SimpleDocTemplate(
                output_filename,
                pagesize=A4,
                topMargin=0.7*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch,
                bottomMargin=0.7*inch
            )
            
            story = []
            
            # Header - Embassy name (top right) - compact
            header_text = 'Embaixada do Brasil em Nova Délhi'
            story.append(Paragraph(header_text, self.header_style))
            story.append(Spacer(1, 0.15*inch))
            
            # Main title - Notas do Dia
            title_text = 'Notas do Dia'
            story.append(Paragraph(title_text, self.title_style))
            
            # Description text
            description_text = "Resumo diário de notas à imprensa do governo indiano"
            story.append(Paragraph(description_text, self.subtitle_style))
            story.append(Spacer(1, 0.05*inch))  # Reduzido de 0.1 para 0.05
            
            # Date - formatted in Portuguese
            today = datetime.now().date()
            month_names = {
                1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
            }
            date_str = f"{today.day} de {month_names[today.month]} de {today.year}"
            story.append(Paragraph(date_str, self.subtitle_style))
            story.append(Spacer(1, 0.08*inch))  # Reduzido de 0.15 para 0.08 (mais compacto)
            
            # Process report text
            lines = report_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Section header
                if line in ['Prime Minister Releases', 
                           'MEA - Press Releases', 
                           'MEA - Speeches & Statements', 
                           'MEA - Media Briefings']:
                    current_section = line
                    # Add section with subtle background
                    section_para = Paragraph(
                        f'<para backColor="#FFFFFF" borderPadding="10" borderWidth="0">'
                        f'<b>{line}</b></para>',
                        self.section_style
                    )
                    story.append(section_para)
                
                # Empty section message
                elif line == "Nenhum item publicado nesta seção desde o último boletim.":
                    story.append(Paragraph(
                        "Nenhum item publicado nesta seção desde o último boletim.",
                        self.empty_style
                    ))
                
                # Document link line: "DD/MM/YYYY - [Title](link)"
                elif re.match(r'\d{2}/\d{2}/\d{4}.*\[.*\]\(.*\)', line):
                    match = re.match(r'(\d{2}/\d{2}/\d{4}) - \[(.*?)\]\((.*?)\)', line)
                    if match:
                        date_str, title, link = match.groups()
                        
                        # Escape HTML special characters in title
                        from xml.sax.saxutils import escape
                        title_escaped = escape(title)
                        
                        # Use same pattern as MEA links - always use Helvetica for links
                        link_text = f'<link href="{link}" color="#2563eb"><b>{date_str}</b> - {title_escaped}</link>'
                        story.append(Paragraph(link_text, self.link_style))
                
                # Summary text
                else:
                    # Use appropriate font based on content
                    font_name = get_appropriate_font(line, is_bold=False)
                    summary_style = ParagraphStyle(
                        'SummaryDynamic',
                        parent=self.summary_style,
                        fontName=font_name
                    )
                    
                    # Add bullet point for summaries
                    formatted_line = f"• {line}" if not line.startswith('•') else line
                    story.append(Paragraph(formatted_line, summary_style))
            
            # Build PDF with callbacks
            doc.build(
                story,
                onFirstPage=lambda c, d: (self._add_background(c, d), self._add_header_footer(c, d)),
                onLaterPages=lambda c, d: (self._add_background(c, d), self._add_header_footer(c, d))
            )
            
            logger.info(f"PDF gerado com sucesso: {output_filename}")
            return output_filename
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

