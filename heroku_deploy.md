# Deploy no Heroku

## 📋 Pré-requisitos

1. Conta no Heroku
2. Heroku CLI instalado: https://devcenter.heroku.com/articles/heroku-cli
3. Git configurado

## 🚀 Deploy Rápido

### 1. **Login no Heroku**
```bash
heroku login
```

### 2. **Criar app no Heroku**
```bash
heroku create notas-do-dia
# ou com nome customizado:
heroku create seu-nome-app
```

### 3. **Adicionar buildpacks necessários**
```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver
```

### 4. **Configurar variáveis de ambiente**
```bash
heroku config:set GOOGLE_API_KEY=sua_chave_api
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USER=seu_email@gmail.com
heroku config:set EMAIL_PASSWORD=sua_senha_app
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_FROM=seu_email@gmail.com
heroku config:set EMAIL_TO=destinatario@email.com
heroku config:set TIMEZONE=Asia/Kolkata
```

**Ou configure todas de uma vez:**
```bash
heroku config:set GOOGLE_API_KEY=sua_chave EMAIL_HOST=smtp.gmail.com EMAIL_PORT=587 EMAIL_USER=seu_email EMAIL_PASSWORD=senha EMAIL_USE_TLS=True EMAIL_FROM=seu_email EMAIL_TO=destinatario TIMEZONE=Asia/Kolkata
```

### 5. **Fazer deploy**
```bash
git push heroku main
```

### 6. **Verificar se está rodando**
```bash
heroku open
# ou
heroku logs --tail
```

## ⏰ Configurar Scheduler (Heroku Scheduler)

Para executar automaticamente todos os dias:

### 1. **Adicionar addon Heroku Scheduler**
```bash
heroku addons:create scheduler:standard
```

### 2. **Configurar job no dashboard**
1. Acesse: https://dashboard.heroku.com/apps/seu-app/scheduler
2. Clique em "Create job"
3. Configure:
   - **Schedule:** `0 6 * * 1-6` (Segunda a sábado às 6h)
   - **Run Command:** `python generate_daily_notes.py`

### 3. **Ou via CLI (se disponível)**
```bash
heroku run python generate_daily_notes.py
```

## 🔍 Comandos Úteis

```bash
# Ver logs
heroku logs --tail

# Executar comando
heroku run python generate_daily_notes.py

# Ver variáveis de ambiente
heroku config

# Verificar status
heroku ps

# Reiniciar app
heroku restart

# Ver informações do app
heroku info
```

## ⚠️ Notas Importantes

1. **Chrome/Selenium:** Os buildpacks do Chrome e ChromeDriver são necessários para o scraper do Prime Minister funcionar.

2. **Timeout:** O Heroku tem timeout de 30 segundos para requests HTTP. Para jobs longos, use o Heroku Scheduler.

3. **Dyno:** O plano gratuito (Hobby) tem limitações. Para produção, considere um plano pago.

4. **Logs:** Os logs são mantidos por 7 dias no plano gratuito.

5. **Variáveis de ambiente:** Todas as variáveis sensíveis devem ser configuradas via `heroku config:set`.

## 🐛 Troubleshooting

### Erro: Chrome não encontrado
```bash
# Verificar buildpacks
heroku buildpacks

# Re-adicionar buildpacks se necessário
heroku buildpacks:clear
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver
```

### Erro: Timeout
- Use Heroku Scheduler para jobs longos
- Considere aumentar o timeout ou usar um dyno maior

### Verificar se Chrome está instalado
```bash
heroku run which google-chrome
heroku run google-chrome --version
```

