from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date
import pytz
from app.config import TIMEZONE
from app.logger import logger

def get_target_dates(today=None):
    tz = pytz.timezone(TIMEZONE)
    if today is None:
        today = datetime.now(tz).date()
    weekday = today.weekday()  # 0=segunda
    if weekday == 0:
        # Segunda: pegar sábado e domingo anteriores
        sat = today - timedelta(days=2)
        sun = today - timedelta(days=1)
        return [sat, sun]
    else:
        # Outros dias: pegar apenas o dia anterior
        return [today - timedelta(days=1)]

def schedule_job(job_func):
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(job_func, 'cron', day_of_week='mon-sat', hour=8, minute=0)
    logger.info("Agendamento configurado: segunda a sábado às 8h (domingo excluído).")
    scheduler.start()
    return scheduler
