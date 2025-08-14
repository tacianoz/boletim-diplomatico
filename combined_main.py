from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.loksabha_scraper import get_weekly_loksabha_summary
from app.loksabha_summarizer import LokSabhaSummarizer
from app.loksabha_scheduler import schedule_loksabha_job, get_loksabha_week_dates
from app.scheduler import schedule_job, get_target_dates
from app.emailer import send_email
from app.logger import logger
import time
from datetime import datetime, timedelta
import pytz
from app.config import TIMEZONE

def run_boletim_only():
    """Executa apenas o boletim diplomático"""
    logger.info("Iniciando execução do Boletim Diplomático...")
    try:
        from generate_pdf import create_pdf_boletim
        
        boletim_pdf = create_pdf_boletim()
        if boletim_pdf:
            # Enviar apenas o boletim
            today = datetime.now().date()
            email_subject = f"Boletim Diplomático - {today.strftime('%d/%m/%Y')}"
            email_body = f"""Prezados/as colegas,

Segue o Boletim Diplomático de {today.strftime('%d/%m/%Y')}.

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi"""
            
            send_email(
                subject=email_subject,
                body=email_body,
                attachments=[boletim_pdf]
            )
            logger.info("Boletim Diplomático enviado com sucesso.")
        else:
            logger.error("Erro ao gerar PDF do Boletim")
            
    except Exception as e:
        logger.error(f"Erro na execução do Boletim Diplomático: {e}")
        send_email(
            subject="Erro no Boletim Diplomático",
            body=f"Ocorreu um erro durante a execução do Boletim Diplomático: {str(e)}"
        )

def run_combined_report():
    """Executa ambos os relatórios e envia no mesmo e-mail"""
    logger.info("Iniciando execução dos relatórios combinados...")
    try:
        from generate_and_send_combined import generate_and_send_combined
        
        success = generate_and_send_combined()
        if success:
            logger.info("Execução dos relatórios combinados concluída com sucesso.")
        else:
            logger.error("Erro na execução dos relatórios combinados.")
            
    except Exception as e:
        logger.error(f"Erro na execução dos relatórios combinados: {e}")
        # Enviar email de erro
        send_email(
            subject="Erro nos Relatórios Combinados",
            body=f"Ocorreu um erro durante a execução dos relatórios combinados: {str(e)}"
        )

def main():
    """Função principal que agenda ambos os serviços"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.config import TIMEZONE
    
    # Criar um único scheduler para ambos os serviços
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    
    # Agendar relatório combinado (segunda-feira às 6h - boletim + loksabha)
    scheduler.add_job(run_combined_report, 'cron', day_of_week='mon', hour=6, minute=0)
    
    # Agendar apenas boletim diplomático (terça a sábado às 6h)
    scheduler.add_job(run_boletim_only, 'cron', day_of_week='tue-sat', hour=6, minute=0)
    
    # Iniciar o scheduler
    scheduler.start()
    
    logger.info("Agendamento configurado:")
    logger.info("- Segunda-feira às 6h: Boletim Diplomático + Lok Sabha")
    logger.info("- Terça a Sábado às 6h: Apenas Boletim Diplomático")
    logger.info("Aguardando execuções...")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Encerrando serviços.")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
