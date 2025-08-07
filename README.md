# Boletim Diplomático – Scraper e Resumidor Automático

Este app Python faz scraping diário de comunicados, discursos e briefings do Ministério de Relações Exteriores da Índia, resume com IA local (LLaMA 3 ou similar) e envia por e-mail.

## Funcionalidades
- Scraping robusto de três seções do site do MEA Índia
- Processamento inteligente de datas (segunda-feira pega sexta, sábado e domingo)
- Sumarização e extração de temas com modelo local (LLaMA 3 ou similar via `transformers`)
- Envio automático por e-mail via SMTP seguro
- Agendamento automático (segunda a sexta, 8h local)
- Logging de execução e falhas

## Estrutura de Pastas
```
boletim_diplomatico/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── scraper.py
│   ├── summarizer.py
│   ├── emailer.py
│   ├── scheduler.py
│   └── logger.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Configuração
1. **Clone o repositório:**
   ```bash
   git clone <repo_url>
   cd boletim_diplomatico
   ```
2. **Crie e edite o arquivo `.env` a partir do exemplo:**
   ```bash
   cp .env.example .env
   # Edite com suas credenciais e configurações
   ```
3. **Instale as dependências:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Baixe o modelo LLaMA 3 ou similar (instruções no summarizer.py).**

## Execução Local
```bash
python main.py
```

## Deploy em Nuvem (Azure App Service)
- Certifique-se de definir variáveis de ambiente no painel do Azure conforme `.env.example`.
- Use `requirements.txt` e `main.py` como entrypoint.
- Configure agendamento via Azure Functions ou mantenha o scheduler local.

## Logs
- Logs de execução e falhas são salvos em `logs/boletim.log`.

## Contato
Dúvidas: <seu_email@dominio.gov.br> 