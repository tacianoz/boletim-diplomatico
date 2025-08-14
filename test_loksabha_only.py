#!/usr/bin/env python3
"""
Script de teste específico apenas para a funcionalidade da Lok Sabha
"""

from app.loksabha_scraper import get_weekly_loksabha_summary
from app.loksabha_summarizer import LokSabhaSummarizer
from app.logger import logger
from datetime import datetime, timedelta
import os

def test_loksabha_scraping():
    """Testa apenas o scraping da Lok Sabha"""
    logger.info("=== TESTE DE SCRAPING LOK SABHA ===")
    
    try:
        print("🔍 Testando scraping da Lok Sabha...")
        questions = get_weekly_loksabha_summary()
        
        if not questions:
            logger.warning("Nenhuma question encontrada para teste")
            print("⚠️  Nenhuma question encontrada para o período de teste")
            return False, []
        
        logger.info(f"✅ Encontradas {len(questions)} questions para teste")
        print(f"✅ Encontradas {len(questions)} questions para teste")
        
        # Mostrar algumas questions encontradas
        print("\n📋 Questions encontradas:")
        for i, question in enumerate(questions[:5]):  # Mostrar apenas as 5 primeiras
            print(f"   {i+1}. {question['title'][:70]}... ({question['date']})")
        
        if len(questions) > 5:
            print(f"   ... e mais {len(questions) - 5} questions")
        
        return True, questions
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de scraping: {e}")
        print(f"❌ Erro no teste de scraping: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_loksabha_summarization(questions):
    """Testa apenas a sumarização da Lok Sabha"""
    logger.info("=== TESTE DE SUMARIZAÇÃO LOK SABHA ===")
    
    try:
        print("\n🤖 Testando sumarização com Google Gemini...")
        summarizer = LokSabhaSummarizer()
        
        # Testar sumarização de uma question
        if questions:
            test_question = questions[0]
            logger.info(f"Testando sumarização de: {test_question['title'][:50]}...")
            
            summary = summarizer.summarize_question(test_question)
            logger.info(f"Resumo gerado: {summary[:100]}...")
            print(f"✅ Resumo gerado: {summary[:100]}...")
            
            # Mostrar resumo completo
            print(f"\n📄 Resumo completo:")
            print(f"   {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de sumarização: {e}")
        print(f"❌ Erro no teste de sumarização: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_loksabha_report(questions):
    """Testa a geração do relatório completo da Lok Sabha"""
    logger.info("=== TESTE DE RELATÓRIO LOK SABHA ===")
    
    try:
        print("\n📊 Gerando relatório completo...")
        summarizer = LokSabhaSummarizer()
        report = summarizer.compile_weekly_report(questions)
        
        # Mostrar parte do relatório
        lines = report.split('\n')
        print(f"\n📄 Relatório gerado ({len(lines)} linhas):")
        for line in lines[:15]:  # Primeiras 15 linhas
            print(f"   {line}")
        if len(lines) > 15:
            print(f"   ... e mais {len(lines) - 15} linhas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de relatório: {e}")
        print(f"❌ Erro no teste de relatório: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_loksabha_pdf():
    """Testa apenas a geração do PDF da Lok Sabha"""
    logger.info("=== TESTE DE PDF LOK SABHA ===")
    
    try:
        print("\n📄 Testando geração de PDF da Lok Sabha...")
        from generate_loksabha_pdf import create_loksabha_pdf
        
        pdf_file = create_loksabha_pdf()
        
        if pdf_file:
            logger.info(f"✅ PDF da Lok Sabha gerado com sucesso: {pdf_file}")
            print(f"✅ PDF da Lok Sabha gerado com sucesso: {pdf_file}")
            print(f"📁 Localização: {os.path.abspath(pdf_file)}")
            return True
        else:
            logger.warning("❌ Erro ao gerar PDF da Lok Sabha")
            print("❌ Erro ao gerar PDF da Lok Sabha")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de PDF: {e}")
        print(f"❌ Erro no teste de PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_loksabha_functionality():
    """Testa toda a funcionalidade da Lok Sabha"""
    logger.info("=== TESTE COMPLETO DA FUNCIONALIDADE LOK SABHA ===")
    
    print("🚀 Iniciando teste completo da Lok Sabha...")
    print("="*60)
    
    # 1. Testar scraping
    scraping_success, questions = test_loksabha_scraping()
    
    if not scraping_success:
        print("\n❌ Teste de scraping falhou. Abortando outros testes.")
        return False
    
    print("\n" + "="*60 + "\n")
    
    # 2. Testar sumarização
    summarization_success = test_loksabha_summarization(questions)
    
    print("\n" + "="*60 + "\n")
    
    # 3. Testar relatório
    report_success = test_loksabha_report(questions)
    
    print("\n" + "="*60 + "\n")
    
    # 4. Testar PDF
    pdf_success = test_loksabha_pdf()
    
    print("\n" + "="*60 + "\n")
    
    # Resumo final
    all_success = scraping_success and summarization_success and report_success and pdf_success
    
    if all_success:
        print("🎉 Teste da Lok Sabha concluído com sucesso!")
        print("✅ Todas as funcionalidades estão operacionais")
        print("\n📊 Resumo:")
        print(f"   - Scraping: ✅ ({len(questions)} questions encontradas)")
        print(f"   - Sumarização: ✅")
        print(f"   - Relatório: ✅")
        print(f"   - PDF: ✅")
        
        # Mostrar período testado
        if questions:
            dates = [q['date'] for q in questions]
            start_date = min(dates)
            end_date = max(dates)
            print(f"\n📅 Período testado: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
        
        return True
        
    else:
        print("❌ Teste da Lok Sabha falhou")
        print("📊 Resumo:")
        print(f"   - Scraping: {'✅' if scraping_success else '❌'}")
        print(f"   - Sumarização: {'✅' if summarization_success else '❌'}")
        print(f"   - Relatório: {'✅' if report_success else '❌'}")
        print(f"   - PDF: {'✅' if pdf_success else '❌'}")
        return False

if __name__ == "__main__":
    success = test_loksabha_functionality()
    if success:
        print("\n✅ Todos os testes da Lok Sabha passaram!")
        print("🚀 Sistema da Lok Sabha pronto para uso em produção")
    else:
        print("\n❌ Alguns testes da Lok Sabha falharam. Verifique os logs.")
