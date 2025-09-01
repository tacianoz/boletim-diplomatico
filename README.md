# Boletim Diplomático – Scraper e Resumidor Automático

Sistema Python que faz scraping diário de comunicados diplomáticos do governo da Índia, resume com Google Gemini AI e gera PDFs elegantes para envio automático por e-mail.

## 🚀 Funcionalidades

### 📰 **Boletim Diplomático Diário**
- Scraping de 4 seções oficiais: Prime Minister Releases, MEA Press Releases, Speeches & Statements, Media Briefings
- **Selenium inteligente:** No primeiro dia do mês, acessa automaticamente o mês anterior para buscar documentos
- Processamento inteligente de datas (segunda-feira pega sábado e domingo)
- Múltiplos seletores para máxima compatibilidade

### 🏛️ **Relatório Semanal Lok Sabha**
- Scraping semanal das questions & answers da Lok Sabha ao MEA
- Busca questions da semana anterior (segunda a domingo)
- Execução automática toda segunda-feira às 6h

### 🤖 **IA e Processamento**
- Sumarização com Google Gemini 1.5 Flash
- **IA inteligente:** Resumos sempre em 2-3 frases (4-5 apenas para documentos excepcionalmente longos)
- **Política de idiomas:** Apenas inglês + excepcionalmente hindi no resumo final
- **Tradução automática:** Outras línguas convertidas para inglês

### 📄 **Geração de PDF com Suporte Unicode**
- Layout profissional com fundo azul claro
- **Suporte completo a scripts indianos:** Hindi, Tamil, Malayalam, Bengali, etc.
- **Lógica inteligente:** Hindi usa fonte Unicode, inglês usa Helvetica
- **Margens otimizadas:** Superior reduzida para melhor aproveitamento do espaço
- **Fonte aumentada:** Resumos em 11pt para melhor legibilidade

### 📧 **Sistema de E-mail Dinâmico**
- Envio automático via Gmail SMTP
- **E-mails inteligentes:** Texto dinâmico baseado no conteúdo disponível
- **Segunda-feira:** E-mail combinado com ambos os PDFs (ou apenas boletim se não há Lok Sabha)
- **Terça a Sábado:** Boletim diplomático normal

### ⏰ **Agendamento Inteligente**
- **Segunda-feira às 6h:** Boletim (sábado e domingo) + Lok Sabha (semana anterior)
- **Terça a Sábado às 6h:** Apenas Boletim (dia anterior)
- Domingo excluído

## 📁 Estrutura do Projeto

```
boletim-diplomatico/
├── app/                    # Módulo principal
│   ├── scraper.py         # Scraping do boletim (com Selenium)
│   ├── loksabha_scraper.py # Scraping da Lok Sabha
│   ├── summarizer.py      # Sumarização do boletim
│   ├── loksabha_summarizer.py # Sumarização da Lok Sabha
│   ├── emailer.py         # Sistema de e-mails
│   ├── font_manager.py    # Gerenciamento de fontes Unicode
│   └── logger.py          # Sistema de logs
├── generate_pdf.py        # Geração de PDF do boletim
├── generate_loksabha_pdf.py # Geração de PDF da Lok Sabha
├── generate_and_send_combined.py # E-mail combinado
├── main.py               # Aplicação principal
└── requirements.txt      # Dependências
```

## ⚙️ Configuração Rápida

### 1. **Clone e configure**
```bash
git clone https://github.com/tacianoz/boletim-diplomatico.git
cd boletim-diplomatico
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. **Configure as variáveis**
```bash
cp env.example .env
# Edite .env com suas credenciais:
# - GOOGLE_API_KEY (Google AI Studio)
# - EMAIL_* (Gmail SMTP)
```

### 3. **Teste**
```bash
python generate_pdf.py                  # Teste do boletim
python generate_loksabha_pdf.py         # Teste da Lok Sabha
```

## 🚀 Execução

### **Manual**
```bash
python generate_and_send_combined.py    # Ambos os PDFs + e-mail
python main.py                          # Apenas boletim
python loksabha_main.py                 # Apenas Lok Sabha
```

### **Automático**
```bash
python combined_main.py                 # Agendamento completo
```

## 📧 Exemplos de E-mail

### **Segunda-feira (com Lok Sabha)**
```
Prezados/as colegas,

Segue em anexo:

1. Boletim Diplomático de 29/08/2025
2. Relatório Semanal Lok Sabha de 18/08/2025 a 24/08/2025

Atenciosamente,
```

### **Terça a Sábado**
```
Prezados/as colegas,

Segue o Boletim Diplomático de 29/08/2025.

Atenciosamente,
```

## 🔧 Tecnologias

- **Python 3.8+**
- **BeautifulSoup4** - Scraping HTML
- **Selenium** - Navegação web e seleção de mês
- **Google Gemini API** - Sumarização com IA
- **ReportLab** - Geração de PDFs
- **APScheduler** - Agendamento
- **SMTP** - Envio de e-mails

## 🐳 Deploy

### **Google Cloud Run**
```bash
gcloud run deploy boletim-diplomatico \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Docker Local**
```bash
docker build -t boletim-diplomatico .
docker run -p 8080:8080 boletim-diplomatico
```

## 📊 Logs

- **Arquivo:** `logs/boletim.log`
- **Rotação:** Semanal
- **Níveis:** INFO, ERROR, DEBUG

## 🆕 Melhorias Recentes

- ✅ **Selenium implementado:** Acesso automático ao mês anterior no primeiro dia
- ✅ **Resumos concisos:** Sempre 2-3 frases (4-5 apenas para documentos longos)
- ✅ **Layout otimizado:** Margens reduzidas e fonte aumentada para melhor legibilidade
- ✅ **Política de idiomas:** Apenas inglês + excepcionalmente hindi
- ✅ **Fontes Unicode completas:** Suporte a todos os scripts indianos
- ✅ **E-mails dinâmicos:** Texto adaptado ao conteúdo disponível
- ✅ **Docker otimizado:** Chrome + fontes incluídas para Selenium

---

**Desenvolvido para a Embaixada do Brasil em Nova Délhi** 