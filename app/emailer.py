import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from app.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_USE_TLS, EMAIL_FROM, EMAIL_TO
from app.logger import logger
import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'services', 'logo_email.png')


def send_email(subject: str, body: str, attachment_path: str = None, attachments: list = None, html_body: str = None):
    msg = MIMEMultipart('related')
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject

    # Build alternative part (plain text + HTML)
    alt = MIMEMultipart('alternative')
    alt.attach(MIMEText(body, 'plain', 'utf-8'))
    if html_body:
        alt.attach(MIMEText(html_body, 'html', 'utf-8'))
    msg.attach(alt)

    # Embed logo as CID inline image
    if html_body and os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as f:
            logo = MIMEImage(f.read(), _subtype='png')
        logo.add_header('Content-ID', '<logo>')
        logo.add_header('Content-Disposition', 'inline', filename='logo.png')
        msg.attach(logo)

    logger.info(f"Enviando email - CWD: {os.getcwd()}")

    # Adicionar anexos se fornecidos
    if attachments:
        for att_path in attachments:
            _attach_file(msg, att_path)
    elif attachment_path:
        _attach_file(msg, attachment_path)

    try:
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


def _attach_file(msg, path):
    if not os.path.exists(path):
        alt = os.path.join(os.getcwd(), 'logs', os.path.basename(path))
        if os.path.exists(alt):
            path = alt
        else:
            logger.error(f"Arquivo nao encontrado: {path}")
            return

    with open(path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(path)}"')
    msg.attach(part)
    logger.info(f"Anexo adicionado: {path}")
