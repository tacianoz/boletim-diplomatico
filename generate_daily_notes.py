#!/usr/bin/env python3
"""
Main script to generate Notas do Dia - India
Uses new scraper architecture
"""
from app.core.scraper_factory import get_mea_scraper, get_pm_scraper
from app.core.date_utils import get_target_dates
from app.services.summarizer import Summarizer
from app.services.pdf_generator import PDFGenerator
from app.emailer import send_email
from app.logger import logger
from datetime import datetime
import pytz


def generate_daily_notes(target_dates=None):
    """
    Generate Notas do Dia for target dates
    
    Args:
        target_dates: List of dates to scrape. If None, uses get_target_dates()
    
    Returns:
        Path to generated PDF file, or None if error
    """
    logger.info("=== GERANDO NOTAS DO DIA - INDIA ===")
    
    try:
        # Get target dates (handles Monday logic automatically if not provided)
        if target_dates is None:
            target_dates = get_target_dates()
        logger.info(f"Buscando documentos para datas: {target_dates}")
        
        # Get scrapers
        mea_scraper = get_mea_scraper()
        pm_scraper = get_pm_scraper()
        
        # Collect all documents
        all_docs = []
        
        # Prime Minister Releases
        logger.info("Buscando Prime Minister Releases...")
        pm_docs = pm_scraper.get_pm_releases(target_dates)
        all_docs.extend(pm_docs)
        
        # MEA Press Releases
        logger.info("Buscando MEA Press Releases...")
        mea_press = mea_scraper.get_press_releases(target_dates)
        all_docs.extend(mea_press)
        
        # MEA Speeches & Statements
        logger.info("Buscando MEA Speeches & Statements...")
        mea_speeches = mea_scraper.get_speeches_statements(target_dates)
        all_docs.extend(mea_speeches)
        
        # MEA Media Briefings
        logger.info("Buscando MEA Media Briefings...")
        mea_briefings = mea_scraper.get_media_briefings(target_dates)
        all_docs.extend(mea_briefings)
        
        if not all_docs:
            logger.info("Nenhum documento encontrado para as datas especificadas.")
            return None
        
        logger.info(f"Total de documentos encontrados: {len(all_docs)}")
        
        # Generate summaries
        logger.info("Gerando resumos com Google Gemini...")
        summarizer = Summarizer()
        report_text = summarizer.compile_report(all_docs)
        
        # Generate PDF
        logger.info("Gerando PDF...")
        pdf_generator = PDFGenerator()
        today = datetime.now().date()
        filename = f"notas_do_dia_{today.strftime('%Y%m%d')}.pdf"
        pdf_file = pdf_generator.generate(all_docs, report_text, filename)
        
        if not pdf_file:
            logger.error("Erro ao gerar PDF")
            return None
        
        logger.info(f"PDF gerado com sucesso: {pdf_file}")
        return pdf_file
        
    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_and_send():
    """Generate Notas do Dia and send via email"""
    pdf_file = generate_daily_notes()
    
    if not pdf_file:
        logger.error("Não foi possível gerar o PDF")
        return False
    
    try:
        # Format date for email
        today = datetime.now().date()
        date_str = today.strftime('%d/%m/%Y')
        
        email_subject = f"Notas do Dia - India - {date_str}"
        email_body = f"""Prezados/as colegas,

Seguem as notas do dia do governo indiano publicadas em {date_str}.

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi"""
        
        send_email(
            subject=email_subject,
            body=email_body,
            attachment_path=pdf_file
        )
        
        logger.info("E-mail enviado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        return False


if __name__ == "__main__":
    success = generate_and_send()
    if success:
        print("\n✅ Notas do Dia gerado e enviado com sucesso!")
    else:
        print("\n❌ Erro no processo. Verifique os logs.")

