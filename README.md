# Notas do Dia – Scraper e Resumidor Automático

Sistema Python que faz scraping diário de comunicados diplomáticos do governo da Índia, resume com Google Gemini 2.0 Flash e gera PDFs elegantes para envio automático por e-mail.

## 🚀 Funcionalidades

### 📰 **Notas do Dia**
- Scraping de 4 seções oficiais:
  - Prime Minister Releases
  - MEA Press Releases
  - MEA Speeches & Statements
  - MEA Media Briefings

### 🤖 **IA e Processamento**
- Sumarização com Google Gemini 2.0 Flash
- **IA inteligente:** Resumos sempre em 2-3 frases (4-5 apenas para documentos excepcionalmente longos)
- **Política de idiomas:** Apenas inglês + excepcionalmente hindi no resumo final
- **Tradução automática:** Outras línguas convertidas para inglês

### 📄 **Geração de PDF Moderna e Clean**
- Design moderno, clean e profissional
- Layout elegante com excelente legibilidade
- **Suporte completo a scripts indianos:** Hindi, Tamil, Malayalam, Bengali, etc.
- **Lógica inteligente:** Hindi usa fonte Unicode, inglês usa Helvetica
- Tipografia melhorada com hierarquia clara
- Cores sutis e profissionais
- Seções bem delimitadas visualmente

### 📧 **Sistema de E-mail**
- Envio automático via Gmail SMTP
- E-mails com PDF anexo

### ⏰ **Agendamento Inteligente**
- **Segunda-feira às 6h:** Notas do Dia (sábado e domingo)
- **Terça a Sábado às 6h:** Notas do Dia (dia anterior)
- Domingo excluído

## 📁 Estrutura do Projeto

```
notas-do-dia/
├── app/                    # Módulo principal
│   ├── core/               # Utilitários e factories
│   │   ├── date_utils.py   # Utilitários de data
│   │   └── scraper_factory.py # Factory para scrapers
│   ├── domain/             # Modelos de domínio
│   │   ├── document.py     # Modelo de documento
│   │   └── report.py       # Modelo de relatório
│   ├── infrastructure/     # Camada de infraestrutura
│   │   └── scrapers/       # Scrapers
│   │       ├── base_scraper.py # Classe base
│   │       ├── mea_scraper.py  # Scraper MEA
│   │       └── pm_scraper.py   # Scraper Prime Minister
│   ├── services/           # Camada de serviços
│   │   ├── summarizer.py  # Sumarização
│   │   └── pdf_generator.py # Geração de PDF
│   ├── emailer.py         # Sistema de e-mails
│   ├── font_manager.py    # Gerenciamento de fontes Unicode
│   ├── logger.py          # Sistema de logs
│   └── config.py          # Configurações
├── generate_daily_notes.py # Script principal
├── generate_pdf.py        # Script legado (deprecated)
├── app_web.py             # API web Flask
├── main.py                # Aplicação principal
└── requirements.txt       # Dependências
```

## ⚙️ Configuração Rápida

### 1. **Clone e configure**
```bash
git clone https://github.com/tacianoz/notas-do-dia.git
cd notas-do-dia
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. **Configure as variáveis**
```bash
cp config/env.example .env
# Edite .env com suas credenciais:
# - GOOGLE_API_KEY (Google AI Studio)
# - EMAIL_* (Gmail SMTP)
```

### 3. **Teste**
```bash
python generate_daily_notes.py  # Gerar Notas do Dia
```

## 🚀 Execução

### **Manual**
```bash
python generate_daily_notes.py  # Gerar e enviar Notas do Dia
python app_web.py               # Iniciar API web
```

### **API Web**
```bash
# Iniciar servidor
python app_web.py

# Endpoints disponíveis:
# POST /generate/daily - Gerar Notas do Dia diário
# POST /generate/yesterday - Gerar para ontem
# POST /generate/custom - Gerar para data específica
```

## 🔧 Tecnologias

- **Python 3.11+**
- **BeautifulSoup4** - Scraping HTML
- **Selenium** - Navegação web e seleção de mês (Prime Minister)
- **Google Gemini 2.0 Flash API** - Sumarização com IA
- **ReportLab** - Geração de PDFs
- **Flask** - API web
- **SMTP** - Envio de e-mails

## ⏰ Agendamento Local (Cron)

Para executar automaticamente todos os dias (exceto domingo) às 6h da manhã:

### **Opção 1: Script Automático (Recomendado)**
```bash
./setup_cron.sh
```

### **Opção 2: Manual**
```bash
# Editar crontab
crontab -e

# Adicionar linha (ajuste o caminho conforme necessário):
# Segunda a sábado às 6h (horário local)
0 6 * * 1-6 cd /caminho/para/notas-do-dia && /caminho/para/venv/bin/python generate_daily_notes.py >> logs/cron.log 2>&1
```

**Nota:** Ajuste o caminho do projeto e do Python conforme seu ambiente.

### **Docker Local (Opcional)**
```bash
cd deploy
docker build -f Dockerfile -t notas-do-dia .
docker run -p 8080:8080 --env-file ../.env notas-do-dia
```

## 📊 Logs

- **Arquivo:** `logs/boletim.log`
- **Rotação:** Semanal
- **Níveis:** INFO, ERROR, DEBUG

## 🆕 Versão 2.0 - Mudanças Principais

### ✅ **Melhorias**
- **Arquitetura refatorada:** Estrutura modular com separação de responsabilidades
- **Scraping robusto:** Retry logic, fallback strategies, múltiplos seletores
- **Design moderno:** PDF com layout clean e profissional
- **Código limpo:** Remoção de funcionalidades desnecessárias

### 🗑️ **Removido**
- Lok Sabha scraper e funcionalidades relacionadas
- UN Statements scraper
- Environment scraper
- Funcionalidades combinadas

### 📝 **Renomeado**
- "Boletim Diplomático" → "Notas do Dia"
- Estrutura de pastas reorganizada

## 🚀 Status Atual

### **✅ Sistema em Execução Local**
- **Ambiente:** Local (Python + Cron)
- **Agendamento:** Segunda a sábado às 6h (via cron)
- **Status:** ✅ Funcionando

### **📊 Seções Ativas**
1. **Prime Minister Releases** - Scraping com Selenium (quando necessário)
2. **MEA - Press Releases** - Scraping tradicional
3. **MEA - Speeches & Statements** - Scraping tradicional
4. **MEA - Media Briefings** - Scraping tradicional

---

**Desenvolvido para a Embaixada do Brasil em Nova Délhi**
