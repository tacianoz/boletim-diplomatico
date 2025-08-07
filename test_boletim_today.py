#!/usr/bin/env python3
"""
Script de teste para executar o boletim com documentos de hoje
"""

from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.emailer import send_email
from app.logger import logger
from datetime import datetime, date

def test_boletim_today():
    logger.info("=== INICIANDO TESTE DO BOLETIM COM DOCUMENTOS DE HOJE ===")
    
    try:
        # Buscar documentos de hoje (para teste)
        today = date.today()
        target_dates = [today]
        logger.info(f"Buscando documentos para hoje: {today}")
        
        docs = get_documents_for_dates(target_dates)
        logger.info(f"Encontrados {len(docs)} documentos de hoje")
        
        if not docs:
            logger.info("Nenhum documento encontrado para hoje. Buscando documentos recentes...")
            # Buscar documentos dos últimos 7 dias
            from datetime import timedelta
            recent_dates = [today - timedelta(days=i) for i in range(7)]
            docs = get_documents_for_dates(recent_dates)
            logger.info(f"Encontrados {len(docs)} documentos dos últimos 7 dias")
        
        if not docs:
            logger.info("Nenhum documento encontrado. Enviando e-mail informativo.")
            send_email(
                subject="Boletim Diplomático – Teste (Sem documentos)",
                body="Nenhum documento foi encontrado no site do MEA Índia nos últimos 7 dias."
            )
            return
        
        # Limitar a 3 documentos para teste
        docs = docs[:3]
        logger.info(f"Processando {len(docs)} documentos para teste")
        
        # Buscar conteúdo completo de cada documento
        logger.info("Buscando conteúdo completo dos documentos...")
        for i, doc in enumerate(docs):
            logger.info(f"Processando documento {i+1}/{len(docs)}: {doc['title'][:50]}...")
            doc['content'] = fetch_full_content(doc['link'])
            if not doc['content']:
                logger.warning(f"Conteúdo vazio para: {doc['title']}")
                doc['content'] = "Conteúdo não disponível para este documento."
        
        # Gerar resumos com Google Gemini
        logger.info("Gerando resumos com Google Gemini...")
        summarizer = Summarizer()
        report = summarizer.compile_report(docs)
        
        # Mostrar o relatório no terminal
        logger.info("=== RELATÓRIO GERADO ===")
        print("\n" + "="*50)
        print("BOLETIM DIPLOMÁTICO - MEA ÍNDIA")
        print("="*50)
        print(report)
        print("="*50)
        
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_boletim_today() 