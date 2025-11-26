#!/bin/bash

# Script de deploy para o Notas do Dia
# Versão 2.0 - Arquitetura refatorada

set -e

# Configurações
PROJECT_ID="gen-lang-client-0413045052"  # Project ID do Google Cloud
REGION="asia-south1"
SERVICE_NAME="notas-do-dia"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Iniciando deploy do Notas do Dia..."
echo "📋 Projeto: $PROJECT_ID"
echo "🌍 Região: $REGION"
echo "🐳 Serviço: $SERVICE_NAME"

# Verificar se o projeto está configurado
if [ "$PROJECT_ID" = "SEU_PROJECT_ID_AQUI" ]; then
    echo "❌ ERRO: Configure o PROJECT_ID no script deploy.sh"
    exit 1
fi

# Verificar se o gcloud está configurado
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERRO: Google Cloud SDK não está instalado"
    exit 1
fi

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build da imagem Docker (a partir da raiz do projeto)
echo "🏗️ Build da imagem Docker..."
cd ..
docker build -f deploy/Dockerfile -t $IMAGE_NAME .
cd deploy

# Push para Container Registry
echo "📤 Enviando imagem para Container Registry..."
docker push $IMAGE_NAME

# Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 1 \
    --set-env-vars TIMEZONE=Asia/Kolkata

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo "✅ Deploy concluído com sucesso!"
echo "🌐 URL do serviço: $SERVICE_URL"
echo "📊 Para ver logs: gcloud logs tail --service=$SERVICE_NAME"
echo "🔧 Para atualizar: ./deploy.sh" 