# 🚀 Deploy no Google Cloud

Este guia explica como fazer deploy do Boletim Diplomático no Google Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud** com billing ativado
2. **Google Cloud SDK** instalado
3. **Docker** instalado (opcional, para build local)

## 🔧 Configuração Inicial

### 1. Instalar Google Cloud SDK
```bash
# Windows
# Baixe de: https://cloud.google.com/sdk/docs/install

# Linux/Mac
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Login e Configuração
```bash
# Login
gcloud auth login

# Listar projetos
gcloud projects list

# Definir projeto (substitua pelo seu Project ID)
gcloud config set project SEU-PROJECT-ID
```

### 3. Habilitar APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## 🚀 Deploy Automático

### Opção 1: Script de Deploy
```bash
# Editar o PROJECT_ID no deploy.sh
nano deploy.sh

# Executar deploy
chmod +x deploy.sh
./deploy.sh
```

### Opção 2: Cloud Build
```bash
# Trigger manual
gcloud builds submit --config cloudbuild.yaml .

# Ou configurar trigger automático no console
```

### Opção 3: Deploy Manual
```bash
# Build e deploy direto
gcloud run deploy boletim-diplomatico \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 1
```

## ⚙️ Configuração de Variáveis de Ambiente

Após o deploy, configure as variáveis no console do Google Cloud Run:

1. Acesse: [Cloud Run Console](https://console.cloud.google.com/run)
2. Selecione o serviço `boletim-diplomatico`
3. Vá em "EDIT & DEPLOY NEW REVISION"
4. Em "Variables & Secrets", adicione:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
EMAIL_USE_TLS=True
EMAIL_FROM=seu-email@gmail.com
EMAIL_TO=destinatario@email.com
GOOGLE_API_KEY=sua-chave-api-google
TIMEZONE=Asia/Kolkata
```

## 📅 Configurar Agendamento

### Opção 1: Cloud Scheduler
```bash
# Criar job agendado
gcloud scheduler jobs create http boletim-daily \
    --schedule="0 6 * * *" \
    --uri="https://seu-servico-url" \
    --http-method=POST \
    --location=us-central1
```

### Opção 2: Cron no Compute Engine
Se preferir uma VM, configure cron:
```bash
# Adicionar ao crontab
0 6 * * * curl -X POST https://seu-servico-url
```

## 💰 Custos Estimados

- **Cloud Run**: ~$5-10/mês (execução diária)
- **Cloud Build**: ~$1-2/mês (deploy)
- **Total**: ~$6-12/mês

## 🔍 Monitoramento

### Logs
```bash
# Ver logs em tempo real
gcloud logs tail --service=boletim-diplomatico

# Ver logs específicos
gcloud logging read "resource.type=cloud_run_revision"
```

### Métricas
- Acesse: [Cloud Run Metrics](https://console.cloud.google.com/run)
- Monitore: requests, latency, memory usage

## 🛠️ Troubleshooting

### Erro de Build
```bash
# Ver logs do build
gcloud builds log BUILD_ID
```

### Erro de Runtime
```bash
# Ver logs do serviço
gcloud run services logs read boletim-diplomatico
```

### Problemas de Email
- Verificar se as credenciais estão corretas
- Testar conectividade SMTP
- Verificar logs de erro

## 🔄 Atualizações

Para atualizar o código:
```bash
# Re-deploy automático
./deploy.sh

# Ou via Cloud Build
gcloud builds submit --config cloudbuild.yaml .
```

## 📞 Suporte

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)

