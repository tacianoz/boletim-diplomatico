# Changelog - Boletim Diplomático

## [2.0.0] - 2025-09-01

### 🚀 **Novas Funcionalidades**
- **Selenium implementado:** Acesso automático ao mês anterior no primeiro dia do mês
- **Resumos concisos:** Sempre 2-3 frases (4-5 apenas para documentos excepcionalmente longos)
- **Layout otimizado:** Margens reduzidas e fonte aumentada para melhor legibilidade

### 🔧 **Melhorias Técnicas**
- **Scraper inteligente:** Detecta automaticamente quando usar seleção de mês
- **Chrome headless:** Configurado para execução em containers
- **Dependências atualizadas:** Selenium + webdriver-manager
- **Docker otimizado:** Chrome + fontes incluídas

### 📊 **Configurações de Deploy**
- **Recursos aumentados:** 4Gi RAM, 2 CPU para suportar Selenium
- **Timeout estendido:** 3600s para operações complexas
- **Cloud Build atualizado:** Configurações otimizadas

### 🗑️ **Removido**
- **Playwright:** Substituído por Selenium
- **Transformers/Torch:** Não mais necessários
- **OpenAI:** Substituído por Google Gemini
- **Configurações desnecessárias:** Simplificação do env.example

### 📝 **Documentação**
- **README atualizado:** Reflete todas as mudanças
- **DEPLOY.md reformulado:** Instruções claras para Selenium
- **deploy.sh melhorado:** Script robusto com verificações
- **CHANGELOG.md:** Este arquivo

---

## [1.0.0] - 2025-08-29

### 🎉 **Lançamento Inicial**
- Sistema básico de scraping
- Sumarização com IA
- Geração de PDFs
- Sistema de e-mails
- Agendamento automático

---

**Desenvolvido para a Embaixada do Brasil em Nova Délhi**
