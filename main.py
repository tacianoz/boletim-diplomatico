from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.emailer import send_email
from app.scheduler import get_target_dates, schedule_job
from app.logger import logger
import time

def run_boletim():
    logger.info("Iniciando execução do Boletim Diplomático...")
    try:
        target_dates = get_target_dates()
        docs = get_documents_for_dates(target_dates)
        if not docs:
            logger.info("Nenhum documento encontrado para as datas alvo.")
            return
        # Buscar conteúdo completo
        for doc in docs:
            doc['content'] = fetch_full_content(doc['link'])
        summarizer = Summarizer()
        report = summarizer.compile_report(docs)
        send_email(
            subject="Boletim Diplomático – MEA Índia",
            body=report
        )
        logger.info("Execução concluída com sucesso.")
    except Exception as e:
        logger.error(f"Erro na execução do boletim: {e}")

def main():
    schedule_job(run_boletim)
    logger.info("Boletim agendado. Aguardando execuções...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Encerrando serviço.")

if __name__ == "__main__":
    main()
