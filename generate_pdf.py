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
import os
import re

def create_pdf_boletim():
    logger.info("=== GERANDO PDF DO BOLETIM DIPLOMÁTICO ===")
    
    try:
        # Buscar documentos do dia anterior
        today = date.today()
        yesterday = today - timedelta(days=1)
        target_dates = [yesterday]
        logger.info(f"Buscando documentos para: {yesterday}")
        
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
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=15,
            alignment=1,  # Center
            textColor=HexColor('#1f4e79'),
            fontName='Arial-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=1,  # Center
            textColor=HexColor('#2e5984'),
            fontName='Arial'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=14,
            alignment=4,  # Justify
            fontName='Arial'
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
            fontName='Arial'
        )
        
        description_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=25,
            leading=14,
            alignment=1,  # Center
            fontStyle='italic',
            fontName='Arial'
        )
        
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=13,
            spaceAfter=8,
            spaceBefore=15,
            textColor=HexColor('#2e5984'),
            fontName='Arial-Bold'
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
            fontName='Arial'
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=0,
            alignment=2,  # Right align
            textColor=HexColor('#666666'),
            fontName='Arial'
        )
        
        # Cabeçalho
        story.append(Paragraph("Boletim Diplomático", title_style))
        
        # Data formatada em português
        month_names = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        day = today.day
        month = month_names[today.month]
        year = today.year
        date_str = f"{day} {month} {year}"
        story.append(Paragraph(date_str, subtitle_style))
        
        # Descrição
        story.append(Paragraph("Resumo diário de notas à imprensa, discursos, comunicados e \"media briefings\" da chancelaria indiana.", description_style))
        
        # Processar o relatório
        lines = report.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Seção principal (ex: "Press Releases")
            if line in ['Press Releases', 'Speeches & Statements', 'Media Briefings']:
                current_section = line
                story.append(Paragraph(current_section, section_style))
            elif line == "Nenhum item publicado ontem nesta seção.":
                story.append(Paragraph(line, empty_section_style))
            elif re.match(r'\d{2}/\d{2}/\d{4} - \[.*\]\(.*\)', line):
                # Linha com data e link: "07/08/2025 - [Title](link)"
                match = re.match(r'(\d{2}/\d{2}/\d{4}) - \[(.*?)\]\((.*?)\)', line)
                if match:
                    date_str, title, link = match.groups()
                    # Criar link clicável
                    link_text = f'{date_str} - {title}'
                    link_para = Paragraph(f'<link href="{link}">{link_text}</link>', link_style)
                    story.append(link_para)
            else:
                # Resumo ou texto normal - adicionar hífens para justificação
                if line and not line.startswith('•'):
                    # Adicionar hífen no início se não for uma lista
                    formatted_line = f"— {line}"
                else:
                    formatted_line = line
                story.append(Paragraph(formatted_line, normal_style))
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph("Embaixada do Brasil em Nova Délhi", footer_style))
        
        # Gerar PDF
        doc.build(story)
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