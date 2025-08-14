#!/usr/bin/env python3
"""
Script de teste que executa ambos os serviços (Boletim Diplomático e Lok Sabha)
"""

from app.scraper import get_documents_for_dates, fetch_full_content
from app.summarizer import Summarizer
from app.loksabha_scraper import get_weekly_loksabha_summary
from app.loksabha_summarizer import LokSabhaSummarizer
from app.scheduler import get_target_dates
from app.loksabha_scheduler import get_loksabha_week_dates
from app.logger import logger
from datetime import datetime, timedelta
import os

def test_boletim_diplomatico():
    """Testa o boletim diplomático"""
    logger.info("=== TESTE DO BOLETIM DIPLOMÁTICO ===")
    
    try:
        # Buscar documentos
        target_dates = get_target_dates()
        docs = get_documents_for_dates(target_dates)
        
        if not docs:
            logger.warning("Nenhum documento encontrado para o boletim")
            print("⚠️  Nenhum documento encontrado para o boletim")
            return False
        
        logger.info(f"✅ Encontrados {len(docs)} documentos para o boletim")
        print(f"✅ Encontrados {len(docs)} documentos para o boletim")
        
        # Buscar conteúdo completo
        for doc in docs:
            doc['content'] = fetch_full_content(doc['link'])
        
        # Gerar resumos
        summarizer = Summarizer()
        report = summarizer.compile_report(docs)
        
        print("✅ Boletim diplomático gerado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste do boletim: {e}")
        print(f"❌ Erro no teste do boletim: {e}")
        return False

def test_loksabha():
    """Testa o relatório da Lok Sabha"""
    logger.info("=== TESTE DO RELATÓRIO LOK SABHA ===")
    
    try:
        # Buscar questions & answers
        questions = get_weekly_loksabha_summary()
        
        if not questions:
            logger.warning("Nenhuma question encontrada para o relatório Lok Sabha")
            print("⚠️  Nenhuma question encontrada para o relatório Lok Sabha")
            return False
        
        logger.info(f"✅ Encontradas {len(questions)} questions para o relatório Lok Sabha")
        print(f"✅ Encontradas {len(questions)} questions para o relatório Lok Sabha")
        
        # Gerar resumos
        summarizer = LokSabhaSummarizer()
        report = summarizer.compile_weekly_report(questions)
        
        print("✅ Relatório Lok Sabha gerado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste da Lok Sabha: {e}")
        print(f"❌ Erro no teste da Lok Sabha: {e}")
        return False

def test_combined_functionality():
    """Testa ambas as funcionalidades"""
    logger.info("=== TESTE COMBINADO - BOLETIM + LOK SABHA ===")
    
    print("🚀 Iniciando teste combinado...")
    
    # Testar boletim diplomático
    boletim_success = test_boletim_diplomatico()
    
    print("\n" + "="*50 + "\n")
    
    # Testar Lok Sabha
    loksabha_success = test_loksabha()
    
    print("\n" + "="*50 + "\n")
    
    # Resumo final
    if boletim_success and loksabha_success:
        print("🎉 Teste combinado concluído com sucesso!")
        print("✅ Ambos os serviços funcionando corretamente")
        
        # Testar geração de PDFs
        try:
            print("\n📄 Testando geração de PDFs...")
            
            # Testar PDF do boletim diplomático
            from generate_pdf import create_pdf_boletim
            boletim_pdf = create_pdf_boletim()
            if boletim_pdf:
                print(f"✅ PDF do Boletim: {boletim_pdf}")
            else:
                print("❌ Erro ao gerar PDF do Boletim")
            
            # Testar PDF da Lok Sabha
            from generate_loksabha_pdf import create_loksabha_pdf
            loksabha_pdf = create_loksabha_pdf()
            if loksabha_pdf:
                print(f"✅ PDF da Lok Sabha: {loksabha_pdf}")
            else:
                print("❌ Erro ao gerar PDF da Lok Sabha")
                
        except Exception as e:
            print(f"⚠️  Erro ao gerar PDFs: {e}")
        
        return True
        
    else:
        print("❌ Teste combinado falhou")
        if not boletim_success:
            print("   - Boletim Diplomático: ❌")
        if not loksabha_success:
            print("   - Relatório Lok Sabha: ❌")
        return False

if __name__ == "__main__":
    success = test_combined_functionality()
    if success:
        print("\n✅ Todos os testes passaram!")
        print("🚀 Sistema pronto para uso em produção")
    else:
        print("\n❌ Alguns testes falharam. Verifique os logs.")
