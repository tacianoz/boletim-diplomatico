#!/usr/bin/env python3
"""
Teste básico para verificar se a aplicação está funcionando
"""
import sys
from app_web import app
from app.core.date_utils import get_target_dates
from app.core.scraper_factory import get_mea_scraper, get_pm_scraper
from app.logger import logger

def test_imports():
    """Testa se os módulos principais podem ser importados"""
    print("=" * 60)
    print("TESTE 1: Verificando imports dos módulos principais...")
    print("=" * 60)
    
    try:
        # Testar imports
        from app.core.date_utils import get_target_dates
        from app.core.scraper_factory import get_mea_scraper, get_pm_scraper
        from app.services.summarizer import Summarizer
        from app.services.html_generator import HTMLGenerator
        from app.emailer import send_email
        
        print("✅ Todos os módulos principais importados com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar módulos: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_target_dates():
    """Testa a função de obter datas alvo"""
    print("\n" + "=" * 60)
    print("TESTE 2: Verificando função get_target_dates()...")
    print("=" * 60)
    
    try:
        dates = get_target_dates()
        print(f"✅ Datas alvo obtidas: {dates}")
        return True
    except Exception as e:
        print(f"❌ Erro ao obter datas alvo: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scrapers():
    """Testa se os scrapers podem ser inicializados"""
    print("\n" + "=" * 60)
    print("TESTE 3: Verificando inicialização dos scrapers...")
    print("=" * 60)
    
    try:
        mea_scraper = get_mea_scraper()
        pm_scraper = get_pm_scraper()
        print("✅ Scrapers inicializados com sucesso!")
        print(f"   - MEA Scraper: {type(mea_scraper).__name__}")
        print(f"   - PM Scraper: {type(pm_scraper).__name__}")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar scrapers: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_app():
    """Testa se o Flask app pode ser iniciado e responder"""
    print("\n" + "=" * 60)
    print("TESTE 4: Verificando Flask app...")
    print("=" * 60)
    
    try:
        # Criar cliente de teste
        with app.test_client() as client:
            # Testar endpoint /health
            response = client.get('/health')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Endpoint /health respondeu: {data}")
                return True
            else:
                print(f"❌ Endpoint /health retornou status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erro ao testar Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("🧪 TESTE GERAL DA APLICAÇÃO NOTAS DO DIA")
    print("=" * 60 + "\n")
    
    results = []
    
    # Executar testes
    results.append(("Imports", test_imports()))
    results.append(("Datas alvo", test_target_dates()))
    results.append(("Scrapers", test_scrapers()))
    results.append(("Flask App", test_flask_app()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
    print("=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

