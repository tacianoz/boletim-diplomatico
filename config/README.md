# Configuração de Variáveis de Ambiente

Esta pasta contém os arquivos de exemplo e configuração para variáveis de ambiente.

## 📁 Arquivos

### `env.example`
Arquivo de exemplo com todas as variáveis de ambiente necessárias para o projeto.

## ⚙️ Configuração

1. **Copie o arquivo de exemplo:**
   ```bash
   cp config/env.example .env
   ```

2. **Edite o arquivo `.env`** com suas credenciais:
   ```bash
   # Google Gemini API
   GOOGLE_API_KEY=sua_chave_aqui
   
   # Email (Gmail SMTP)
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASS=sua_senha_app
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_FROM=seu_email@gmail.com
   EMAIL_TO=destinatario@example.com
   
   # Timezone
   TIMEZONE=Asia/Kolkata
   ```

3. **Importante:** O arquivo `.env` deve estar na **raiz do projeto** (não nesta pasta), pois o código procura por ele lá.

## 🔒 Segurança

- **NUNCA** commite o arquivo `.env` no Git
- O arquivo `.env` já está no `.gitignore`
- Use `env.example` como referência para documentar novas variáveis

## 📝 Variáveis Obrigatórias

- `GOOGLE_API_KEY` - Chave da API do Google Gemini (obrigatório)
- `EMAIL_USER` - Email para envio (obrigatório)
- `EMAIL_PASS` - Senha do app do Gmail (obrigatório)
- `EMAIL_TO` - Destinatário do email (obrigatório)

## 📝 Variáveis Opcionais

- `TIMEZONE` - Timezone (padrão: `Asia/Kolkata`)
- `LOG_LEVEL` - Nível de log (padrão: `INFO`)
- `EMAIL_HOST` - Host SMTP (padrão: `smtp.gmail.com`)
- `EMAIL_PORT` - Porta SMTP (padrão: `587`)
- `EMAIL_USE_TLS` - Usar TLS (padrão: `True`)
- `EMAIL_FROM` - Email remetente (padrão: `EMAIL_USER`)

