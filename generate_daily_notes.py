#!/usr/bin/env python3
"""
Main script to generate Notas do Dia - India
Uses new scraper architecture
"""
from app.core.scraper_factory import get_mea_scraper, get_pm_scraper
from app.core.date_utils import get_target_dates
from app.services.summarizer import Summarizer
from app.services.html_generator import HTMLGenerator
from app.services.theme_classifier import classify_all
from app.emailer import send_email
from app.logger import logger
from datetime import datetime
import pytz
import os


def generate_daily_notes(target_dates=None):
    """
    Generate Notas do Dia for target dates

    Args:
        target_dates: List of dates to scrape. If None, uses get_target_dates()

    Returns:
        HTML string with the email body, or None if error
    """
    logger.info("=== GERANDO NOTAS DO DIA - INDIA ===")

    try:
        if target_dates is None:
            target_dates = get_target_dates()
        logger.info(f"Buscando documentos para datas: {target_dates}")

        mea_scraper = get_mea_scraper()
        pm_scraper = get_pm_scraper()

        all_docs = []

        logger.info("Buscando Prime Minister Releases...")
        all_docs.extend(pm_scraper.get_pm_releases(target_dates))

        logger.info("Buscando MEA Press Releases...")
        all_docs.extend(mea_scraper.get_press_releases(target_dates))

        logger.info("Buscando MEA Speeches & Statements...")
        all_docs.extend(mea_scraper.get_speeches_statements(target_dates))

        logger.info("Buscando MEA Media Briefings...")
        all_docs.extend(mea_scraper.get_media_briefings(target_dates))

        if not all_docs:
            logger.info("Nenhum documento encontrado para as datas especificadas.")
            return None

        logger.info(f"Total de documentos encontrados: {len(all_docs)}")

        # Generate summaries (adds 'summary' key to each doc)
        summarizer = Summarizer()
        summarizer.compile_report(all_docs)

        # Classify documents by theme
        logger.info("Classificando documentos por tema...")
        classify_all(all_docs)
        brasil_count = sum(1 for d in all_docs if d.get('brasil'))
        if brasil_count:
            logger.info(f"Documentos relacionados ao Brasil: {brasil_count}")

        # Generate daily synthesis in diplomatic Portuguese
        logger.info("Gerando síntese do dia...")
        synthesis = summarizer.generate_daily_synthesis(all_docs, target_dates)

        # Generate HTML email body
        logger.info("Gerando HTML...")
        html_generator = HTMLGenerator()
        html = html_generator.generate(all_docs, target_dates, synthesis)

        # Save to archive
        archive_dir = os.path.join(os.getcwd(), 'logs', 'arquivo')
        os.makedirs(archive_dir, exist_ok=True)
        dates_str = '_'.join(d.strftime('%Y%m%d') for d in sorted(target_dates))
        archive_path = os.path.join(archive_dir, f'notas_{dates_str}.html')
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Edição salva no arquivo: {archive_path}")

        return html

    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_and_send():
    """Generate Notas do Dia and send via email"""
    from app.config import TIMEZONE
    import pytz

    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()

    if today.weekday() == 6:  # Domingo
        logger.info("Domingo detectado - pulando geração (roda apenas de segunda a sábado)")
        return False

    target_dates = get_target_dates()
    html_body = generate_daily_notes(target_dates)

    if not html_body:
        logger.error("Não foi possível gerar o HTML")
        return False

    try:
        if len(target_dates) > 1:
            date_str = " e ".join([d.strftime('%d/%m/%Y') for d in sorted(target_dates)])
        else:
            publication_date = target_dates[0] if target_dates else datetime.now().date()
            date_str = publication_date.strftime('%d/%m/%Y')

        send_email(
            subject=f"Notas do dia - {date_str}",
            body=f"Notas do Dia - {date_str}",
            html_body=html_body,
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

