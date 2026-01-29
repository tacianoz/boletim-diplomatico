# Notas do Dia – Scraper e Resumidor Automático

Sistema Python que faz scraping diário de comunicados diplomáticos do governo da Índia, resume com **Google Gemini 2.5 Flash** e gera PDFs para envio automático por e-mail.

## Funcionalidades

### Scraping
- **Prime Minister Releases** - via Selenium (site requer JavaScript)
- **MEA Press Releases**
- **MEA Speeches & Statements**
- **MEA Media Briefings**

### Sumarização com IA
- **Google Gemini 2.5 Flash** (padrão)
- **Ollama** (opcional, modelo local)
- Resumos de 40-50 palavras em inglês
- Extração de conteúdo via iframe para PM releases

### PDF e E-mail
- PDF com design clean e profissional
- Suporte a scripts indianos (Hindi, Tamil, etc.)
- Envio automático via Gmail SMTP

### Agendamento
- **Segunda-feira 6h IST:** Notas de sábado e domingo
- **Terça a Sábado 6h IST:** Notas do dia anterior
- **Domingo:** Pula automaticamente

## Configuração

### 1. Clone e instale
```bash
git clone https://github.com/tacianoz/notas-do-dia.git
cd notas-do-dia/apps/notas-do-dia
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure o .env
```bash
cp config/env.example .env
```

Edite `.env`:
```env
# Sumarização (gemini ou ollama)
SUMMARIZER_PROVIDER=gemini
GOOGLE_API_KEY=sua_api_key_aqui
GEMINI_MODEL=gemini-2.5-flash

# E-mail
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_app_password
EMAIL_RECIPIENTS=destinatario1@email.com,destinatario2@email.com

# Opcional: Ollama (se SUMMARIZER_PROVIDER=ollama)
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral
```

### 3. Teste
```bash
python generate_daily_notes.py
```

## Docker

### Build e execução
```bash
cd /caminho/para/notas-do-dia
docker-compose up -d --build
```

### Executar manualmente
```bash
docker exec notas-do-dia python generate_daily_notes.py
```

### Reiniciar (após mudar .env)
```bash
docker-compose restart
```

### Logs
```bash
docker logs -f notas-do-dia
```

## Estrutura

```
notas-do-dia/
├── app/
│   ├── infrastructure/scrapers/
│   │   ├── base_scraper.py
│   │   ├── mea_scraper.py
│   │   └── pm_scraper.py
│   ├── services/
│   │   ├── summarizer.py
│   │   └── pdf_generator.py
│   ├── config.py
│   └── emailer.py
├── generate_daily_notes.py
├── app_web.py
└── deploy/Dockerfile
```

## Tecnologias

- Python 3.11+
- Selenium + ChromeDriver (webdriver-manager)
- Google Gemini API
- BeautifulSoup4
- ReportLab (PDF)
- Flask (API web)

---

**Desenvolvido para a Embaixada do Brasil em Nova Délhi**
