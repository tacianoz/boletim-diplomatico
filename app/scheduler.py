from apscheduler.schedulers.background import BackgroundScheduler
from app.config import TIMEZONE
from app.logger import logger

def schedule_job(job_func):
    """Schedule a job to run Monday to Saturday at 6 AM"""
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(job_func, 'cron', day_of_week='mon-sat', hour=6, minute=0)
    logger.info("Agendamento configurado: segunda a sábado às 6h (domingo excluído).")
    scheduler.start()
    return scheduler
