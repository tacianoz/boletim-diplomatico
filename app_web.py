#!/usr/bin/env python3
"""
Versão web do Boletim Diplomático para testes manuais
"""

from flask import Flask, request, jsonify
from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.emailer import send_email
from app.logger import logger
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>📰 Boletim Diplomático - MEA Índia</h1>
    <p>API para geração e envio do boletim diplomático</p>
    
    <h2>Endpoints:</h2>
    <ul>
        <li><strong>GET /health</strong> - Verificar status do serviço</li>
        <li><strong>POST /generate</strong> - Gerar boletim para hoje</li>
        <li><strong>POST /generate/yesterday</strong> - Gerar boletim para ontem</li>
        <li><strong>POST /generate/daily</strong> - Gerar boletim diário (com lógica de segunda-feira)</li>
        <li><strong>POST /generate/custom</strong> - Gerar boletim para data específica</li>
    </ul>
    
    <h2>Exemplo de uso:</h2>
    <pre>
    curl -X POST https://seu-servico-url/generate
    </pre>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "boletim-diplomatico"
    })

@app.route('/generate', methods=['POST'])
def generate_today():
    """Gerar boletim para hoje"""
    try:
        today = date.today()
        return generate_boletim([today])
    except Exception as e:
        logger.error(f"Erro ao gerar boletim para hoje: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/yesterday', methods=['POST'])
def generate_yesterday():
    """Gerar boletim para ontem"""
    try:
        yesterday = date.today() - timedelta(days=1)
        return generate_boletim([yesterday])
    except Exception as e:
        logger.error(f"Erro ao gerar boletim para ontem: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/daily', methods=['POST'])
def generate_daily():
    """Gerar boletim diário com lógica de segunda-feira"""
    try:
        # Usar fuso horário da Índia
        import pytz
        tz = pytz.timezone('Asia/Kolkata')
        today = datetime.now(tz).date()
        weekday = today.weekday()  # 0=Segunda, 1=Terça, ..., 6=Domingo
        
        if weekday == 0:  # Segunda-feira
            # Buscar sábado e domingo
            saturday = today - timedelta(days=2)
            sunday = today - timedelta(days=1)
            target_dates = [saturday, sunday]
            logger.info(f"Segunda-feira: buscando sábado ({saturday}) e domingo ({sunday})")
            
            # Segunda-feira: gerar boletim + loksabha
            return generate_combined_report(target_dates)
        else:
            # Outros dias: buscar apenas o dia anterior
            yesterday = today - timedelta(days=1)
            target_dates = [yesterday]
            logger.info(f"{today.strftime('%A')}: buscando ontem ({yesterday})")
            
            # Outros dias: apenas boletim
            return generate_boletim(target_dates)
    except Exception as e:
        logger.error(f"Erro ao gerar boletim diário: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/custom', methods=['POST'])
def generate_custom():
    """Gerar boletim para data específica"""
    try:
        data = request.get_json()
        if not data or 'date' not in data:
            return jsonify({"error": "Data não fornecida. Use: {'date': 'YYYY-MM-DD'}"}), 400
        
        target_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        return generate_boletim([target_date])
    except Exception as e:
        logger.error(f"Erro ao gerar boletim para data customizada: {e}")
        return jsonify({"error": str(e)}), 500

def generate_combined_report(target_dates):
    """Função para gerar boletim + loksabha (segunda-feira)"""
    logger.info(f"Gerando relatório combinado para datas: {target_dates}")
    
    pdf_files = []
    
    # 1. Gerar PDF do Boletim Diplomático
    logger.info("1. Gerando PDF do Boletim Diplomático...")
    try:
        # Buscar documentos
        docs = get_documents_for_dates(target_dates)
        if docs:
            # Buscar conteúdo completo
            for i, doc in enumerate(docs):
                logger.info(f"Processando documento {i+1}/{len(docs)}: {doc['title'][:50]}...")
                doc['content'] = fetch_full_content(doc['link'])
            
            # Gerar resumos
            logger.info("Gerando resumos com Google Gemini...")
            summarizer = Summarizer()
            report = summarizer.compile_report(docs)
            
            # Gerar PDF
            from generate_pdf import create_pdf_boletim
            boletim_pdf = create_pdf_boletim()
            if boletim_pdf:
                pdf_files.append(boletim_pdf)
                logger.info(f"✅ PDF do Boletim gerado: {boletim_pdf}")
        else:
            logger.warning("Nenhum documento encontrado para o boletim")
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF do Boletim: {e}")
    
    # 2. Gerar PDF da Lok Sabha
    logger.info("2. Gerando PDF da Lok Sabha...")
    try:
        from generate_loksabha_pdf import create_loksabha_pdf
        loksabha_pdf = create_loksabha_pdf()
        if loksabha_pdf:
            pdf_files.append(loksabha_pdf)
            logger.info(f"✅ PDF da Lok Sabha gerado: {loksabha_pdf}")
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF da Lok Sabha: {e}")
    
    # 3. Enviar e-mail com ambos os anexos
    if pdf_files:
        try:
            # Calcular período da Lok Sabha para o e-mail
            loksabha_end = datetime.now().date() - timedelta(days=1)  # Domingo
            loksabha_start = loksabha_end - timedelta(days=6)  # Segunda-feira
            
            # Formatar período da Lok Sabha
            loksabha_period = f"{loksabha_start.strftime('%d/%m/%Y')} a {loksabha_end.strftime('%d/%m/%Y')}"
            
            # Formatar período do boletim
            if len(target_dates) == 2:
                boletim_period = f"{target_dates[0].strftime('%d/%m/%Y')} e {target_dates[1].strftime('%d/%m/%Y')}"
            else:
                boletim_period = target_dates[0].strftime('%d/%m/%Y')
            
            # Gerar texto do e-mail baseado no número de PDFs
            if len(pdf_files) == 2:
                # Caso 1: Ambos os PDFs (boletim + loksabha)
                email_subject = f"Boletim Diplomático + Relatório Lok Sabha - {datetime.now().strftime('%d/%m/%Y')}"
                email_body = f"""Prezados/as colegas,

Segue o relatório combinado com:

1. Boletim Diplomático referente às publicações de {boletim_period}
2. Relatório Semanal Lok Sabha de {loksabha_period}

Atenciosamente,
Taciano S. Zimmermann"""
            else:
                # Caso 2: Apenas boletim (sem loksabha)
                email_subject = f"Boletim Diplomático - {datetime.now().strftime('%d/%m/%Y')}"
                email_body = f"""Prezados/as colegas,

Segue o Boletim Diplomático referente às publicações de {boletim_period}.

Nota: Não foram encontrados documentos da Lok Sabha para a semana anterior ({loksabha_period}).

Atenciosamente,
Taciano S. Zimmermann"""
            
            # Enviar e-mail com múltiplos anexos
            from app.emailer import send_email
            send_email(
                subject=email_subject,
                body=email_body,
                attachments=pdf_files
            )
            
            return jsonify({
                "success": True,
                "message": "Relatório combinado gerado e enviado com sucesso!",
                "dates": [str(d) for d in target_dates],
                "pdf_files": pdf_files,
                "email_sent": True
            })
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return jsonify({
                "success": True,
                "message": "Relatório combinado gerado com sucesso, mas erro no envio de e-mail",
                "dates": [str(d) for d in target_dates],
                "pdf_files": pdf_files,
                "email_sent": False,
                "email_error": str(e)
            })
    else:
        return jsonify({
            "success": False,
            "message": "Nenhum PDF foi gerado com sucesso",
            "dates": [str(d) for d in target_dates],
            "pdf_files": []
        })

def generate_boletim(target_dates):
    """Função principal para gerar o boletim"""
    logger.info(f"Gerando boletim para datas: {target_dates}")
    
    # Buscar documentos
    docs = get_documents_for_dates(target_dates)
    if not docs:
        return jsonify({
            "message": "Nenhum documento encontrado para as datas especificadas",
            "dates": [str(d) for d in target_dates],
            "documents_count": 0
        })
    
    # Buscar conteúdo completo
    for i, doc in enumerate(docs):
        logger.info(f"Processando documento {i+1}/{len(docs)}: {doc['title'][:50]}...")
        doc['content'] = fetch_full_content(doc['link'])
    
    # Gerar resumos
    logger.info("Gerando resumos com Google Gemini...")
    summarizer = Summarizer()
    report = summarizer.compile_report(docs)
    
    # Gerar PDF
    from generate_pdf import create_pdf_boletim
    pdf_file = create_pdf_boletim()
    
    # Enviar e-mail
    try:
        # Formatar período do boletim
        if len(target_dates) == 2:
            boletim_period = f"{target_dates[0].strftime('%d/%m/%Y')} e {target_dates[1].strftime('%d/%m/%Y')}"
        else:
            boletim_period = target_dates[0].strftime('%d/%m/%Y')
        
        # Usar fuso horário correto (Asia/Kolkata)
        from datetime import datetime
        import pytz
        tz = pytz.timezone('Asia/Kolkata')
        today = datetime.now(tz).date()
        
        email_body = f"""Prezados/as colegas,

Segue o Boletim Diplomático de {today.strftime('%d/%m/%Y')}.

Atenciosamente,
Taciano S. Zimmermann"""
        
        send_email(
            subject=f"Boletim Diplomático - {today.strftime('%d/%m/%Y')}",
            body=email_body,
            attachment_path=pdf_file
        )
        
        return jsonify({
            "success": True,
            "message": "Boletim gerado e enviado com sucesso!",
            "dates": [str(d) for d in target_dates],
            "documents_count": len(docs),
            "pdf_file": pdf_file,
            "email_sent": True
        })
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        return jsonify({
            "success": True,
            "message": "Boletim gerado com sucesso, mas erro no envio de e-mail",
            "dates": [str(d) for d in target_dates],
            "documents_count": len(docs),
            "pdf_file": pdf_file,
            "email_sent": False,
            "email_error": str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
