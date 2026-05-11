# Notas do Dia

Sistema que faz scraping diário de comunicados oficiais do governo da Índia, gera resumos com IA e envia um boletim HTML formatado por e-mail.

## Funcionalidades

### Scraping
- **Prime Minister Releases** (PIB, via Selenium)
- **MEA Press Releases**
- **MEA Speeches & Statements**
- **MEA Media Briefings**

### Sumarização com IA
- **Google Gemini 2.5 Flash** para resumos individuais (50-60 palavras, inglês)
- **Claude Sonnet** para síntese do dia (português diplomático)
- Classificação temática por IA (Gemini)
- Tags: agricultura, defesa, energia, ciência/tecnologia, saúde, comércio, cooperação sul-sul, América Latina, Brasil, BRICS, política externa/interna, economia, regiões

### Email HTML
- Design com identidade visual da Embaixada do Brasil
- Síntese narrativa do dia no topo
- Nomes em negrito
- Tags temáticas coloridas por documento
- Destaque verde + badge para documentos que mencionam o Brasil
- Contador de documentos por seção
- Logo da Embaixada embutida (CID inline)

### Arquivo
- Edições salvas em `logs/arquivo/`
- Endpoint `/arquivo` para consultar edições anteriores

### Agendamento
- **Segunda-feira:** notas de sábado e domingo
- **Terça a sábado:** notas do dia anterior
- **Domingo:** pula automaticamente

## Configuração

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
- `GOOGLE_API_KEY` (Gemini, para resumos e classificação)
- `ANTHROPIC_API_KEY` (Claude, para síntese do dia)
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
- `POST /generate/custom` — data específica (`{"date": "YYYY-MM-DD"}`)
- `GET /arquivo` — listar edições arquivadas

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

**Embaixada do Brasil em Nova Délhi**
