import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_USE_TLS, EMAIL_FROM, EMAIL_TO
from app.logger import logger

def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO.split(','), msg.as_string())
        server.quit()
        logger.info(f"E-mail enviado para {EMAIL_TO}")
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail: {e}")
