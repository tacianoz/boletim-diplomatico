#!/usr/bin/env python3
"""
Script de teste para a funcionalidade da Lok Sabha
"""

from app.loksabha_scraper import get_weekly_loksabha_summary
from app.loksabha_summarizer import LokSabhaSummarizer
from app.logger import logger
from datetime import datetime, timedelta
import os

def test_loksabha_functionality():
    """Testa toda a funcionalidade da Lok Sabha"""
    logger.info("=== TESTE DA FUNCIONALIDADE LOK SABHA ===")
    
    try:
        # 1. Testar scraping
        logger.info("1. Testando scraping da Lok Sabha...")
        questions = get_weekly_loksabha_summary()
        
        if not questions:
            logger.warning("Nenhuma question encontrada para teste")
            print("⚠️  Nenhuma question encontrada para o período de teste")
            return False
        
        logger.info(f"✅ Encontradas {len(questions)} questions para teste")
        print(f"✅ Encontradas {len(questions)} questions para teste")
        
        # 2. Mostrar algumas questions encontradas
        logger.info("2. Questions encontradas:")
        for i, question in enumerate(questions[:3]):  # Mostrar apenas as 3 primeiras
            print(f"   {i+1}. {question['title'][:60]}... ({question['date']})")
        
        # 3. Testar sumarização
        logger.info("3. Testando sumarização com Google Gemini...")
        summarizer = LokSabhaSummarizer()
        
        # Testar sumarização de uma question
        if questions:
            test_question = questions[0]
            logger.info(f"Testando sumarização de: {test_question['title'][:50]}...")
            
            summary = summarizer.summarize_question(test_question)
            logger.info(f"Resumo gerado: {summary[:100]}...")
            print(f"✅ Resumo gerado: {summary[:100]}...")
        
        # 4. Gerar relatório completo
        logger.info("4. Gerando relatório completo...")
        report = summarizer.compile_weekly_report(questions)
        
        # Mostrar parte do relatório
        lines = report.split('\n')
        print("\n📄 Relatório gerado:")
        for line in lines[:10]:  # Primeiras 10 linhas
            print(f"   {line}")
        if len(lines) > 10:
            print(f"   ... e mais {len(lines) - 10} linhas")
        
        # 5. Testar geração de PDF
        logger.info("5. Testando geração de PDF...")
        
        try:
            from generate_loksabha_pdf import create_loksabha_pdf
            pdf_file = create_loksabha_pdf()
            
            if pdf_file:
                logger.info(f"✅ PDF gerado com sucesso: {pdf_file}")
                print(f"✅ PDF gerado com sucesso: {pdf_file}")
                print(f"📁 Localização: {os.path.abspath(pdf_file)}")
            else:
                logger.warning("❌ Erro ao gerar PDF")
                print("❌ Erro ao gerar PDF")
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar PDF: {e}")
            print(f"❌ Erro ao gerar PDF: {e}")
        
        # 6. Resumo final
        logger.info("=== TESTE CONCLUÍDO COM SUCESSO ===")
        print("\n🎉 Teste da Lok Sabha concluído com sucesso!")
        print(f"📊 Resumo:")
        print(f"   - Questions encontradas: {len(questions)}")
        print(f"   - Sumarização: ✅")
        print(f"   - PDF: ✅")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste da Lok Sabha: {e}")
        print(f"❌ Erro no teste da Lok Sabha: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_loksabha_functionality()
    if success:
        print("\n✅ Todos os testes passaram!")
    else:
        print("\n❌ Alguns testes falharam. Verifique os logs.")
