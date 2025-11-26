# Changelog - Notas do Dia

## [2.0.0] - 2025-11-26

### 🚀 **Refatoração Completa**

#### **Mudanças Principais**
- **Renomeado:** "Boletim Diplomático" → "Notas do Dia"
- **Arquitetura refatorada:** Estrutura modular com separação clara de responsabilidades
- **Scraping robusto:** Implementação unificada com retry logic e fallback strategies

#### **Novas Funcionalidades**
- **Design moderno do PDF:** Layout clean, profissional e elegante
- **Scraping robusto:** Retry automático, múltiplos seletores, detecção de erros
- **Estrutura modular:** Core, Domain, Infrastructure, Services layers
- **Factory pattern:** Criação centralizada de scrapers

#### **Melhorias Técnicas**
- **Base Scraper:** Classe base com funcionalidades comuns (retry, timeout, logging)
- **MEA Scraper:** Scraper unificado para todas as seções MEA
- **PM Scraper:** Scraper para Prime Minister com Selenium quando necessário
- **PDF Generator:** Classe dedicada com design moderno
- **Date Utils:** Utilitários centralizados para manipulação de datas

#### **Removido**
- ❌ Lok Sabha scraper e todas as funcionalidades relacionadas
- ❌ UN Statements scraper (UNGA e UNSC)
- ❌ Environment scraper
- ❌ Funcionalidades combinadas (generate_and_send_combined.py)
- ❌ Arquivos antigos de scraping

#### **Arquitetura**
```
app/
├── core/              # Utilitários e factories
├── domain/            # Modelos de domínio
├── infrastructure/    # Scrapers
└── services/          # Sumarização e PDF
```

#### **URLs de Scraping**
- MEA Press Releases: `https://www.mea.gov.in/press-releases.htm?51/Press_Releases`
- MEA Media Briefings: `https://www.mea.gov.in/media-briefings.htm?49/Media_Briefings`
- MEA Speeches: `https://www.mea.gov.in/Speeches-Statements.htm?50/Speeches__amp;_Statements`
- PM Releases: `https://www.pib.gov.in/PMContents/PMContents.aspx?menuid=1&reg=3&lang=1`

### 📝 **Documentação**
- README.md completamente atualizado
- DEPLOY.md atualizado
- CHANGELOG.md criado

---

## [1.0.0] - 2025-09-01

### 🎉 **Lançamento Inicial**
- Sistema básico de scraping
- Sumarização com IA
- Geração de PDFs
- Sistema de e-mails
- Agendamento automático
- Suporte a Lok Sabha, UN Statements e Environment

---

**Desenvolvido para a Embaixada do Brasil em Nova Délhi**
