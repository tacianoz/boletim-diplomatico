from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date
import pytz
from app.config import TIMEZONE
from app.logger import logger

def get_loksabha_week_dates():
    """
    Retorna as datas da semana anterior (segunda a domingo)
    para o relatório da Lok Sabha
    """
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    days_since_monday = today.weekday()  # 0=segunda, 1=terça, ..., 6=domingo
    
    # Última segunda-feira
    last_monday = today - timedelta(days=days_since_monday + 7)
    # Último domingo
    last_sunday = last_monday + timedelta(days=6)
    
    return last_monday, last_sunday

def schedule_loksabha_job(job_func, scheduler=None):
    """
    Agenda o job da Lok Sabha para rodar toda segunda-feira às 6h
    """
    if scheduler is None:
        scheduler = BackgroundScheduler(timezone=TIMEZONE)
        scheduler.start()
    
    scheduler.add_job(job_func, 'cron', day_of_week='mon', hour=6, minute=0)
    logger.info("Agendamento da Lok Sabha configurado: toda segunda-feira às 6h.")
    return scheduler
