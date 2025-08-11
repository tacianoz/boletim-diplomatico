#!/usr/bin/env python3
"""
Script de teste para gerar PDF e enviar por e-mail
"""

from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.emailer import send_email
from app.logger import logger
from datetime import datetime, date, timedelta
import os

def test_generate_and_send():
    logger.info("=== TESTE: GERANDO PDF E ENVIANDO POR E-MAIL ===")
    
    try:
        # Usar lógica de segunda-feira (sábado + domingo)
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
        else:
            # Outros dias: buscar apenas o dia anterior
            yesterday = today - timedelta(days=1)
            target_dates = [yesterday]
            logger.info(f"{today.strftime('%A')}: buscando ontem ({yesterday})")
        
        docs = get_documents_for_dates(target_dates)
        logger.info(f"Encontrados {len(docs)} documentos do dia anterior")
        
        if not docs:
            logger.info("Nenhum documento encontrado para o dia anterior.")
            return None
        
        # Buscar conteúdo completo
        for i, doc in enumerate(docs):
            logger.info(f"Processando documento {i+1}/{len(docs)}: {doc['title'][:50]}...")
            doc['content'] = fetch_full_content(doc['link'])
            if not doc['content']:
                doc['content'] = "Content not available for this document."
        
        # Gerar resumos com Google Gemini
        logger.info("Gerando resumos com Google Gemini...")
        summarizer = Summarizer()
        report = summarizer.compile_report(docs)
        
        # Gerar PDF
        from generate_pdf import create_pdf_boletim
        pdf_file = create_pdf_boletim()
        
        if not pdf_file:
            logger.error("Erro ao gerar PDF")
            return None
            
        logger.info(f"PDF gerado: {pdf_file}")
        
        # Enviar por e-mail
        logger.info("Enviando por e-mail...")
        
        # Criar corpo do e-mail
        email_body = f"""Prezados/as colegas,

Segue o Boletim Diplomático de {today.strftime('%d/%m/%Y')}.

Atenciosamente,
Taciano S. Zimmermann"""
        
        # Enviar e-mail com anexo
        send_email(
            subject=f"Boletim Diplomático - {today.strftime('%d/%m/%Y')}",
            body=email_body,
            attachment_path=pdf_file
        )
        
        logger.info("✅ E-mail enviado com sucesso!")
        return pdf_file
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_generate_and_send()
    if result:
        print(f"\n✅ Teste concluído com sucesso!")
        print(f"📁 PDF: {result}")
    else:
        print("\n❌ Erro no teste") 