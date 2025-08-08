#!/bin/bash

# Script de deploy para Google Cloud Run
# Execute: chmod +x deploy.sh && ./deploy.sh

# Configurações
PROJECT_ID="gen-lang-client-0413045052"  # Project ID do Gemini API
SERVICE_NAME="boletim-diplomatico"
REGION="us-central1"

echo "🚀 Deployando Boletim Diplomático para Google Cloud Run..."

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK não encontrado. Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar se está logado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Não está logado no Google Cloud. Execute: gcloud auth login"
    exit 1
fi

# Definir projeto
echo "📋 Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔧 Habilitando APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build e deploy
echo "🏗️  Fazendo build e deploy..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 1 \
    --set-env-vars "TIMEZONE=Asia/Kolkata"

echo "✅ Deploy concluído!"
echo "🌐 URL do serviço:"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"

echo ""
echo "📧 Configure as variáveis de ambiente no console do Google Cloud Run:"
echo "   - EMAIL_HOST=smtp.gmail.com"
echo "   - EMAIL_PORT=587"
echo "   - EMAIL_USER=seu-email@gmail.com"
echo "   - EMAIL_PASSWORD=sua-senha-de-app"
echo "   - EMAIL_USE_TLS=True"
echo "   - EMAIL_FROM=seu-email@gmail.com"
echo "   - EMAIL_TO=destinatario@email.com"
echo "   - GOOGLE_API_KEY=sua-chave-api"
