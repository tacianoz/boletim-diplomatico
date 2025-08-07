#!/usr/bin/env python3
"""
Script de teste para executar o boletim uma vez manualmente
"""

from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.emailer import send_email
from app.scheduler import get_target_dates
from app.logger import logger
from datetime import datetime

def test_boletim():
    logger.info("=== INICIANDO TESTE DO BOLETIM DIPLOMÁTICO ===")
    
    try:
        # Buscar documentos de ontem (ou sexta/sábado/domingo se for segunda)
        target_dates = get_target_dates()
        logger.info(f"Buscando documentos para as datas: {target_dates}")
        
        docs = get_documents_for_dates(target_dates)
        logger.info(f"Encontrados {len(docs)} documentos")
        
        if not docs:
            logger.info("Nenhum documento encontrado para as datas alvo.")
            # Enviar e-mail informando que não há documentos
            send_email(
                subject="Boletim Diplomático – Teste (Sem documentos)",
                body="Nenhum documento foi encontrado para as datas alvo no site do MEA Índia."
            )
            return
        
        # Buscar conteúdo completo de cada documento
        logger.info("Buscando conteúdo completo dos documentos...")
        for i, doc in enumerate(docs):
            logger.info(f"Processando documento {i+1}/{len(docs)}: {doc['title'][:50]}...")
            doc['content'] = fetch_full_content(doc['link'])
            if not doc['content']:
                logger.warning(f"Conteúdo vazio para: {doc['title']}")
        
        # Gerar resumos com Google Gemini
        logger.info("Gerando resumos com Google Gemini...")
        summarizer = Summarizer()
        report = summarizer.compile_report(docs)
        
        # Enviar e-mail
        logger.info("Enviando e-mail...")
        send_email(
            subject="Boletim Diplomático – MEA Índia (TESTE)",
            body=report
        )
        
        logger.info("=== TESTE CONCLUÍDO COM SUCESSO ===")
        logger.info(f"E-mail enviado com {len(docs)} documentos processados")
        
    except Exception as e:
        logger.error(f"Erro no teste do boletim: {e}")
        # Enviar e-mail de erro
        send_email(
            subject="Erro no Boletim Diplomático – Teste",
            body=f"Ocorreu um erro durante o teste do boletim:\n\n{str(e)}"
        )

if __name__ == "__main__":
    test_boletim() 