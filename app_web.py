#!/usr/bin/env python3
"""
Web API for Notas do Dia - India
"""
from flask import Flask, request, jsonify
from app.core.date_utils import get_target_dates
from app.emailer import send_email
from app.logger import logger
from generate_daily_notes import generate_daily_notes
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>📰 Notas do Dia - India</h1>
    <p>API para geração e envio do Notas do Dia</p>
    
    <h2>Endpoints:</h2>
    <ul>
        <li><strong>GET /health</strong> - Verificar status do serviço</li>
        <li><strong>POST /generate</strong> - Gerar Notas do Dia para hoje</li>
        <li><strong>POST /generate/yesterday</strong> - Gerar Notas do Dia para ontem</li>
        <li><strong>POST /generate/daily</strong> - Gerar Notas do Dia diário (com lógica de segunda-feira)</li>
        <li><strong>POST /generate/custom</strong> - Gerar Notas do Dia para data específica</li>
    </ul>
    
    <h2>Exemplo de uso:</h2>
    <pre>
    curl -X POST https://seu-servico-url/generate/daily
    </pre>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "notas-do-dia-india"
    })

@app.route('/generate', methods=['POST'])
def generate_today():
    """Gerar Notas do Dia para hoje"""
    try:
        today = date.today()
        return _generate_and_send_daily_notes([today])
    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia para hoje: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/yesterday', methods=['POST'])
def generate_yesterday():
    """Gerar Notas do Dia para ontem"""
    try:
        yesterday = date.today() - timedelta(days=1)
        return _generate_and_send_daily_notes([yesterday])
    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia para ontem: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/daily', methods=['POST'])
def generate_daily():
    """Gerar Notas do Dia diário com lógica de segunda-feira"""
    try:
        target_dates = get_target_dates()
        logger.info(f"Buscando Notas do Dia para datas: {target_dates}")
        return _generate_and_send_daily_notes(target_dates)
    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia diário: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/custom', methods=['POST'])
def generate_custom():
    """Gerar Notas do Dia para data específica"""
    try:
        data = request.get_json()
        if not data or 'date' not in data:
            return jsonify({"error": "Data não fornecida. Use: {'date': 'YYYY-MM-DD'}"}), 400
        
        target_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        return _generate_and_send_daily_notes([target_date])
    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia para data customizada: {e}")
        return jsonify({"error": str(e)}), 500

def _generate_and_send_daily_notes(target_dates):
    """Helper function to generate and send Notas do Dia via API"""
    try:
        # Generate PDF using the main function
        pdf_file = generate_daily_notes(target_dates)
        
        if not pdf_file:
            return jsonify({
                "message": "Nenhum documento encontrado para as datas especificadas",
                "dates": [str(d) for d in target_dates],
                "documents_count": 0
            })
        
        # Send email
        try:
            # Format date for email - handle multiple dates (e.g., Saturday and Sunday on Monday)
            if len(target_dates) > 1:
                # Multiple dates: show range (e.g., "23 e 24/11/2025")
                dates_str = " e ".join([d.strftime('%d/%m/%Y') for d in sorted(target_dates)])
                date_str = dates_str
            else:
                # Single date
                publication_date = target_dates[0] if target_dates else datetime.now().date()
                date_str = publication_date.strftime('%d/%m/%Y')
            
            email_subject = f"Notas do Dia - India - {date_str}"
            email_body = f"""Prezados/as colegas,

Seguem as notas do dia do governo indiano publicadas em {date_str}.

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi"""
            
            send_email(
                subject=email_subject,
                body=email_body,
                attachment_path=pdf_file
            )
            
            return jsonify({
                "success": True,
                "message": "Notas do Dia gerado e enviado com sucesso!",
                "dates": [str(d) for d in target_dates],
                "pdf_file": pdf_file,
                "email_sent": True
            })
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return jsonify({
                "success": True,
                "message": "Notas do Dia gerado com sucesso, mas erro no envio de e-mail",
                "dates": [str(d) for d in target_dates],
                "pdf_file": pdf_file,
                "email_sent": False,
                "email_error": str(e)
            })
            
    except Exception as e:
        logger.error(f"Erro ao gerar Notas do Dia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
