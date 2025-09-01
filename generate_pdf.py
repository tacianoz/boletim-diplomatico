#!/usr/bin/env python3
"""
Script para gerar PDF do Boletim Diplomático
"""

from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
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

def create_pdf_boletim():
    logger.info("=== GERANDO PDF DO BOLETIM DIPLOMÁTICO ===")
    
    try:
        # Usar lógica de segunda-feira (sábado + domingo)
        import pytz
        tz = pytz.timezone('Asia/Kolkata')
        today = datetime.now(tz).date()
        weekday = today.weekday()  # 0=Segunda, 1=Terça, ..., 6=Domingo
        
        if weekday == 0:  # Segunda-feira
            # Buscar sábado e domingo
            saturday = today - timedelta(days=2)
            sunday = today - timedelta(days=1)
            target_dates = [saturday, sunday]
            logger.info(f"Segunda-feira: buscando sábado ({saturday}) e domingo ({sunday})")
        else:
            # Outros dias: buscar apenas o dia anterior
            yesterday = today - timedelta(days=1)
            target_dates = [yesterday]
            logger.info(f"{today.strftime('%A')}: buscando dia anterior ({yesterday})")
        
        docs = get_documents_for_dates(target_dates)
        logger.info(f"Encontrados {len(docs)} documentos do dia anterior")
        
        if not docs:
            logger.info("Nenhum documento encontrado para o dia anterior.")
            return None
        
        # Mostrar datas encontradas
        dates_found = set(doc['date'] for doc in docs)
        logger.info(f"Datas encontradas: {sorted(dates_found)}")
        
        # Buscar conteúdo completo
        for i, doc in enumerate(docs):
            logger.info(f"Processando documento {i+1}/{len(docs)}: {doc['title'][:50]}...")
            doc['content'] = fetch_full_content(doc['link'])
            if not doc['content']:
                doc['content'] = "Content not available for this document."
        
        # Gerar resumos com Google Gemini
        logger.info("Gerando resumos com Google Gemini...")
        summarizer = Summarizer()
        report = summarizer.compile_report(docs)
        
        # Criar PDF
        filename = f"boletim_diplomatico_{today.strftime('%Y%m%d')}.pdf"
        doc = SimpleDocTemplate(
            filename, 
            pagesize=A4,
            topMargin=0.5*inch,  # Diminuir margem superior (era padrão ~1 inch)
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        

        
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
            fontSize=11,  # Aumentado de 9 para 11 (era 9)
            spaceAfter=10,
            leading=13,   # Aumentado de 11 para 13 para manter proporção
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
        
        empty_section_style = ParagraphStyle(
            'EmptySection',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=12,
            alignment=1,  # Center
            fontStyle='italic',
            textColor=HexColor('#666666'),
            fontName=UNICODE_FONT
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
            f'Boletim Diplomático</para>', 
            title_style
        )
        story.append(title_with_border)
        
        # Data formatada em português
        month_names = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        day = today.day
        month = month_names[today.month]
        year = today.year
        date_str = f"{day} de {month} de {year}"
        story.append(Paragraph(date_str, subtitle_style))
        
        # Descrição
        story.append(Paragraph("Resumo diário de comunicados diplomáticos do governo indiano.", description_style))
        
        # Processar o relatório
        lines = report.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Debug: log da linha sendo processada
            logger.info(f"Processando linha: {line[:100]}...")
                
            # Seção principal (ex: "Prime Minister Releases")
            if line in ['Prime Minister Releases', 'MEA - Press Releases', 'MEA - Speeches & Statements', 'MEA - Media Briefings', 'UN Statements']:
                current_section = line
                logger.info(f"Aplicando section_style para: {line}")
                story.append(Paragraph(current_section, section_style))
            elif line == "Nenhum item publicado nesta seção desde o último boletim.":
                story.append(Paragraph("Nenhum item publicado nesta seção desde o último boletim.", empty_section_style))
            elif re.match(r'\d{2}/\d{2}/\d{4}.*\[.*\]\(.*\)', line):
                logger.info(f"Match encontrado para link: {line}")
                # Linha com data e link: "07/08/2025 - [Title](link)" ou "07/08/2025 - UNGA - [Title](link)"
                match = re.match(r'(\d{2}/\d{2}/\d{4})(?: - (UNGA|UNSC))? - \[(.*?)\]\((.*?)\)', line)
                if match:
                    date_str, org, title, link = match.groups()
                    logger.info(f"Regex groups: date={date_str}, org={org}, title={title[:50]}..., link={link[:50]}...")
                    # Criar link clicável
                    if org:
                        link_text = f'{date_str} - {org} - {title}'
                    else:
                        link_text = f'{date_str} - {title}'
                    # Usar link_style diretamente para garantir consistência
                    link_para = Paragraph(f'<link href="{link}">{link_text}</link>', link_style)
                    story.append(link_para)
                else:
                    logger.warning(f"Regex não capturou grupos para: {line}")
                    # Tentar regex mais simples para debug
                    simple_match = re.match(r'(\d{2}/\d{2}/\d{4}) - (.*?) - \[(.*?)\]\((.*?)\)', line)
                    if simple_match:
                        logger.info(f"Simple regex match: {simple_match.groups()}")
                    else:
                        logger.warning(f"Nenhum regex funcionou para: {line}")
            else:
                # Resumo ou texto normal - usar estilo dinâmico baseado no conteúdo
                if line.startswith('SPEAKER:'):
                    # Linha do autor - remover o prefixo SPEAKER: e não adicionar hífen
                    formatted_line = line.replace('SPEAKER: ', '')
                elif line and not line.startswith('•'):
                    # Adicionar hífen no início se não for uma lista
                    formatted_line = f"— {line}"
                else:
                    formatted_line = line
                
                # Para resumos, usar fonte fixa para consistência entre ambientes
                summary_style = ParagraphStyle(
                    'Summary',
                    parent=normal_style,
                    fontName='Helvetica'  # Fonte fixa para consistência
                )
                story.append(Paragraph(formatted_line, summary_style))
        
        # Gerar PDF com fundo
        doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
        logger.info(f"PDF gerado com sucesso: {filename}")
        
        return filename
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    pdf_file = create_pdf_boletim()
    if pdf_file:
        print(f"\n✅ PDF gerado com sucesso: {pdf_file}")
        print(f"📁 Localização: {os.path.abspath(pdf_file)}")
    else:
        print("\n❌ Erro ao gerar PDF") 