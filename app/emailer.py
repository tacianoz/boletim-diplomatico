import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from app.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_USE_TLS, EMAIL_FROM, EMAIL_TO
from app.logger import logger
import os

def send_email(subject: str, body: str, attachment_path: str = None, attachments: list = None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Adicionar anexos se fornecidos
    if attachments:
        # Lista de anexos
        for attachment_path in attachments:
            if os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
                logger.info(f"Anexo adicionado: {attachment_path}")
    elif attachment_path and os.path.exists(attachment_path):
        # Anexo único (compatibilidade com versão anterior)
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(attachment_path)}'
        )
        msg.attach(part)
        logger.info(f"Anexo adicionado: {attachment_path}")
    
    try:
        # Usar SSL para porta 465, TLS para porta 587
        if EMAIL_PORT == 465:
            server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
        else:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            if EMAIL_USE_TLS:
                server.starttls()
        
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO.split(','), msg.as_string())
        server.quit()
        logger.info(f"E-mail enviado para {EMAIL_TO}")
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail: {e}")
