from app.loksabha_scraper import get_weekly_loksabha_summary
from app.loksabha_summarizer import LokSabhaSummarizer
from app.loksabha_scheduler import schedule_loksabha_job, get_loksabha_week_dates
from app.emailer import send_email
from app.logger import logger
import time

def run_loksabha_report():
    """Executa o relatório semanal da Lok Sabha"""
    logger.info("Iniciando execução do Relatório Semanal da Lok Sabha...")
    try:
        # Buscar questions & answers da semana anterior
        questions = get_weekly_loksabha_summary()
        
        if not questions:
            logger.info("Nenhuma question & answer encontrada para a semana anterior.")
            # Enviar email informando que não há conteúdo
            send_email(
                subject="Relatório Semanal Lok Sabha - Sem Conteúdo",
                body="Nenhuma question & answer foi encontrada para a semana anterior (segunda a domingo)."
            )
            return
        
        # Gerar resumos com Google Gemini
        summarizer = LokSabhaSummarizer()
        report = summarizer.compile_weekly_report(questions)
        
        # Obter período da semana
        start_date, end_date = get_loksabha_week_dates()
        period_str = f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        
        # Enviar email com o relatório
        email_subject = f"Relatório Semanal Lok Sabha - {period_str}"
        send_email(
            subject=email_subject,
            body=report
        )
        
        logger.info("Relatório semanal da Lok Sabha executado com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro na execução do relatório da Lok Sabha: {e}")
        # Enviar email de erro
        send_email(
            subject="Erro no Relatório Semanal Lok Sabha",
            body=f"Ocorreu um erro durante a execução do relatório semanal da Lok Sabha: {str(e)}"
        )

def main():
    """Função principal que agenda e executa o relatório da Lok Sabha"""
    schedule_loksabha_job(run_loksabha_report)
    logger.info("Relatório da Lok Sabha agendado. Aguardando execuções...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Encerrando serviço da Lok Sabha.")

if __name__ == "__main__":
    main()
