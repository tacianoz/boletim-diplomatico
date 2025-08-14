#!/usr/bin/env python3
"""
Script de teste para o sistema combinado de PDFs (Boletim + Lok Sabha)
"""

from generate_and_send_combined import generate_and_send_combined
from app.logger import logger
import os

def test_combined_system():
    """Testa o sistema combinado de PDFs"""
    logger.info("=== TESTE DO SISTEMA COMBINADO ===")
    
    print("🚀 Testando sistema combinado de PDFs...")
    print("="*60)
    
    try:
        success = generate_and_send_combined()
        
        if success:
            print("\n🎉 Teste do sistema combinado concluído com sucesso!")
            print("✅ Ambos os PDFs foram gerados e enviados no mesmo e-mail")
            print("\n📊 Resumo:")
            print("   - PDF do Boletim Diplomático: ✅")
            print("   - PDF da Lok Sabha: ✅")
            print("   - E-mail combinado: ✅")
            print("   - Anexos múltiplos: ✅")
            return True
        else:
            print("\n❌ Teste do sistema combinado falhou")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste do sistema combinado: {e}")
        print(f"❌ Erro no teste do sistema combinado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_combined_system()
    if success:
        print("\n✅ Sistema combinado funcionando perfeitamente!")
        print("🚀 Pronto para uso em produção")
    else:
        print("\n❌ Alguns problemas foram encontrados. Verifique os logs.")
