# Notas do Dia

Sistema que faz scraping diario de comunicados oficiais do governo da India, gera resumos com IA e envia um boletim HTML formatado por e-mail.

## Funcionalidades

### Scraping
- **Prime Minister Releases** (PIB, via Selenium)
- **MEA Press Releases**
- **MEA Speeches & Statements**
- **MEA Media Briefings**

### Sumarizacao com IA
- **Google Gemini 2.5 Flash** para resumos individuais (50-60 palavras, ingles)
- **Claude Sonnet** para sintese do dia (portugues diplomatico)
- Classificacao tematica por IA (Gemini)
- Tags: agricultura, defesa, energia, ciencia/tecnologia, saude, comercio, cooperacao sul-sul, America Latina, Brasil, BRICS, politica indiana, economia indiana

### Email HTML
- Design com identidade visual da Embaixada do Brasil
- Sintese narrativa do dia no topo
- Nomes em negrito
- Tags tematicas coloridas por documento
- Destaque verde + badge para documentos que mencionam o Brasil
- Contador de documentos por secao
- Logo da Embaixada embutida (CID inline)

### Arquivo
- Edicoes salvas em `logs/arquivo/`
- Endpoint `/arquivo` para consultar edicoes anteriores

### Agendamento
- **Segunda-feira:** notas de sabado e domingo
- **Terca a sabado:** notas do dia anterior
- **Domingo:** pula automaticamente

## Configuracao

### 1. Clone e instale
```bash
git clone https://github.com/tacianoz/notas-do-dia.git
cd notas-do-dia
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure o .env
```bash
cp config/env.example .env
```

Edite `.env` com suas credenciais:
- `SUMMARIZER_PROVIDER=gemini`
- `GOOGLE_API_KEY` (Gemini, para resumos e classificacao)
- `ANTHROPIC_API_KEY` (Claude, para sintese do dia)
- `EMAIL_USER` / `EMAIL_PASSWORD` (Gmail app password)
- `EMAIL_FROM` / `EMAIL_TO`

### 3. Execute
```bash
python generate_daily_notes.py
```

## API Web

```bash
python main.py
```

- `GET /health` — status
- `POST /generate` — gerar para hoje
- `POST /generate/custom` — data especifica (`{"date": "YYYY-MM-DD"}`)
- `GET /arquivo` — listar edicoes arquivadas

## Estrutura

```
notas-do-dia/
├── app/
│   ├── infrastructure/scrapers/
│   │   ├── mea_scraper.py
│   │   └── pm_scraper.py
│   ├── services/
│   │   ├── summarizer.py
│   │   ├── html_generator.py
│   │   └── theme_classifier.py
│   ├── config.py
│   └── emailer.py
├── generate_daily_notes.py
├── app_web.py
└── deploy/Dockerfile
```

## Tecnologias

- Python 3.11+
- Selenium + ChromeDriver
- Google Gemini API
- Anthropic Claude API
- BeautifulSoup4
- Flask

---

**Embaixada do Brasil em Nova Delhi**
