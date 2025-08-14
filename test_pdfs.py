#!/usr/bin/env python3
"""
Script de teste específico para geração de PDFs (Boletim Diplomático e Lok Sabha)
"""

from app.logger import logger
import os

def test_boletim_pdf():
    """Testa a geração do PDF do boletim diplomático"""
    logger.info("=== TESTE PDF DO BOLETIM DIPLOMÁTICO ===")
    
    try:
        from generate_pdf import create_pdf_boletim
        
        print("📄 Gerando PDF do Boletim Diplomático...")
        pdf_file = create_pdf_boletim()
        
        if pdf_file:
            logger.info(f"✅ PDF do Boletim gerado com sucesso: {pdf_file}")
            print(f"✅ PDF do Boletim gerado com sucesso: {pdf_file}")
            print(f"📁 Localização: {os.path.abspath(pdf_file)}")
            return True
        else:
            logger.warning("❌ Erro ao gerar PDF do Boletim")
            print("❌ Erro ao gerar PDF do Boletim")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste do PDF do Boletim: {e}")
        print(f"❌ Erro no teste do PDF do Boletim: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_loksabha_pdf():
    """Testa a geração do PDF da Lok Sabha"""
    logger.info("=== TESTE PDF DA LOK SABHA ===")
    
    try:
        from generate_loksabha_pdf import create_loksabha_pdf
        
        print("📄 Gerando PDF da Lok Sabha...")
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
        logger.error(f"❌ Erro no teste do PDF da Lok Sabha: {e}")
        print(f"❌ Erro no teste do PDF da Lok Sabha: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_pdfs():
    """Testa a geração de ambos os PDFs"""
    logger.info("=== TESTE COMPLETO DE PDFs ===")
    
    print("🚀 Iniciando teste de geração de PDFs...")
    print("="*50)
    
    # Testar PDF do boletim diplomático
    boletim_success = test_boletim_pdf()
    
    print("\n" + "="*50 + "\n")
    
    # Testar PDF da Lok Sabha
    loksabha_success = test_loksabha_pdf()
    
    print("\n" + "="*50 + "\n")
    
    # Resumo final
    if boletim_success and loksabha_success:
        print("🎉 Teste de PDFs concluído com sucesso!")
        print("✅ Ambos os PDFs foram gerados corretamente")
        print("\n📊 Resumo:")
        print("   - PDF do Boletim Diplomático: ✅")
        print("   - PDF da Lok Sabha: ✅")
        return True
        
    else:
        print("❌ Teste de PDFs falhou")
        if not boletim_success:
            print("   - PDF do Boletim Diplomático: ❌")
        if not loksabha_success:
            print("   - PDF da Lok Sabha: ❌")
        return False

if __name__ == "__main__":
    success = test_all_pdfs()
    if success:
        print("\n✅ Todos os PDFs foram gerados com sucesso!")
        print("🚀 Sistema de geração de PDFs funcionando corretamente")
    else:
        print("\n❌ Alguns PDFs falharam. Verifique os logs.")
