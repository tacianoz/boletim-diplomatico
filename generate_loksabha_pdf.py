#!/usr/bin/env python3
"""
Script para gerar PDF do Relatório Semanal da Lok Sabha
"""

from app.loksabha_scraper import get_weekly_loksabha_summary
from app.loksabha_summarizer import LokSabhaSummarizer
from app.logger import logger
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus.flowables import KeepTogether
from reportlab.platypus.flowables import PageBreak, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
import os
import re

# Importar gerenciador de fontes Unicode
from app.font_manager import UNICODE_FONT, UNICODE_FONT_BOLD, get_appropriate_font, contains_unicode_chars

def add_background(canvas, doc):
    """Adiciona fundo azul claro ao documento"""
    canvas.saveState()
    # Azul um pouco mais visível para o fundo
    canvas.setFillColor(HexColor('#f0f4f8'))
    canvas.rect(0, 0, doc.width + doc.leftMargin + doc.rightMargin, 
                doc.height + doc.topMargin + doc.bottomMargin, fill=1)
    canvas.restoreState()

def create_loksabha_pdf():
    logger.info("=== GERANDO PDF DO RELATÓRIO SEMANAL LOK SABHA ===")
    
    try:
        # Buscar questions & answers da semana anterior
        questions = get_weekly_loksabha_summary()
        
        if not questions:
            logger.info("Nenhuma question & answer encontrada para a semana anterior.")
            return None
        
        # Gerar resumos com Google Gemini
        logger.info("Gerando resumos com Google Gemini...")
        summarizer = LokSabhaSummarizer()
        report = summarizer.compile_weekly_report(questions)
        
        # Calcular período da semana anterior
        today = datetime.now().date()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        # Criar PDF
        filename = f"loksabha_weekly_{last_monday.strftime('%Y%m%d')}_{last_sunday.strftime('%Y%m%d')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Função para criar estilo dinâmico baseado no conteúdo
        def create_dynamic_style(base_style, text, is_bold=False):
            """Cria estilo com fonte apropriada baseada no conteúdo"""
            font_name = get_appropriate_font(text, is_bold)
            
            # Retornar estilo com fonte apropriada
            return ParagraphStyle(
                f'Dynamic_{is_bold}',
                parent=base_style,
                fontName=font_name
            )
        
        # Estilo para cabeçalho da embaixada
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=0,
            alignment=2,  # Right align
            textColor=HexColor('#4b5563'),
            fontName='Helvetica-Bold'  # Texto em inglês, usar Helvetica-Bold
        )
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=15,
            alignment=1,  # Center
            textColor=HexColor('#2d3748'),
            fontName='Helvetica-Bold'  # Texto em inglês, usar Helvetica-Bold
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            alignment=1,  # Center
            textColor=HexColor('#374151'),
            fontName=UNICODE_FONT
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=10,
            leading=11,
            alignment=4,  # Justify
            fontName=UNICODE_FONT
        )
        
        link_style = ParagraphStyle(
            'LinkStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14,
            textColor=HexColor('#0066cc'),
            underline=True,
            alignment=0,  # Left align for links
            fontName=UNICODE_FONT
        )
        
        description_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=25,
            leading=12,
            alignment=1,  # Center
            fontStyle='italic',
            fontName=UNICODE_FONT
        )
        
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=13,
            spaceAfter=8,
            spaceBefore=15,
            textColor=HexColor('#2d3748'),
            fontName='Helvetica-Bold'  # Texto em inglês, usar Helvetica-Bold
        )
        
        date_header_style = ParagraphStyle(
            'DateHeader',
            parent=styles['Heading3'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=12,
            textColor=HexColor('#1f2937'),
            fontName='Helvetica-Bold'  # Texto em inglês, usar Helvetica-Bold
        )
        
        # Cabeçalho da embaixada (topo direito) com borda
        header_with_border = Paragraph(
            f'<para borderWidth="1" borderColor="#d1d5db" borderPadding="8" backColor="#f9fafb">'
            f'Embaixada do Brasil em Nova Délhi</para>', 
            header_style
        )
        story.append(header_with_border)
        story.append(Spacer(1, 30))
        
        # Título principal com borda sutil
        title_with_border = Paragraph(
            f'<para borderWidth="2" borderColor="#2d3748" borderPadding="12" backColor="#f8fafc">'
            f'Relatório Semanal - Lok Sabha</para>', 
            title_style
        )
        story.append(title_with_border)
        
        # Período coberto em português
        month_names = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        start_day = last_monday.day
        end_day = last_sunday.day
        month = month_names[last_monday.month]
        year = last_monday.year
        
        if start_day == end_day:
            period_str = f"{start_day} de {month} de {year}"
        else:
            period_str = f"{start_day} a {end_day} de {month} de {year}"
        
        story.append(Paragraph(period_str, subtitle_style))
        
        # Descrição
        story.append(Paragraph("Resumo semanal das questions & answers da Lok Sabha ao Ministério de Relações Exteriores da Índia.", description_style))
        
        # Processar o relatório
        lines = report.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Cabeçalho principal (removido pois já está no título)
            if line == "Lok Sabha Questions & Answers - Weekly Summary":
                # Pular o título pois já está no cabeçalho
                continue
            elif line.startswith("Period:"):
                # Pular a linha de período pois já está no subtítulo
                continue
            elif line.startswith("===") and line.endswith("==="):
                # Cabeçalho de data: "=== Monday, 05 August 2025 ==="
                date_text = line.replace("===", "").strip()
                # Converter para português
                try:
                    # Parsear a data em inglês e converter para português
                    from datetime import datetime
                    # Remover o dia da semana e parsear a data
                    date_part = date_text.split(', ', 1)[1] if ', ' in date_text else date_text
                    date_obj = datetime.strptime(date_part, "%d %B %Y")
                    
                    month_names = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    
                    day = date_obj.day
                    month = month_names[date_obj.month]
                    year = date_obj.year
                    
                    date_text_pt = f"{day} de {month} de {year}"
                    story.append(Paragraph(date_text_pt, date_header_style))
                except:
                    # Se falhar a conversão, usar o texto original
                    story.append(Paragraph(date_text, date_header_style))
            elif re.match(r'\[.*\]\(.*\)', line):
                # Linha com link: "[Title](link)"
                match = re.match(r'\[(.*?)\]\((.*?)\)', line)
                if match:
                    title, link = match.groups()
                    # Criar link clicável
                    link_para = Paragraph(f'<link href="{link}">{title}</link>', link_style)
                    story.append(link_para)
            else:
                # Resumo ou texto normal - adicionar hífens para justificação
                if line and not line.startswith('•'):
                    # Adicionar hífen no início se não for uma lista
                    formatted_line = f"— {line}"
                else:
                    formatted_line = line
                story.append(Paragraph(formatted_line, normal_style))
        
        # Gerar PDF com fundo
        doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
        logger.info(f"PDF gerado com sucesso: {filename}")
        
        return filename
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF da Lok Sabha: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    pdf_file = create_loksabha_pdf()
    if pdf_file:
        print(f"\n✅ PDF da Lok Sabha gerado com sucesso: {pdf_file}")
        print(f"📁 Localização: {os.path.abspath(pdf_file)}")
    else:
        print("\n❌ Erro ao gerar PDF da Lok Sabha")
