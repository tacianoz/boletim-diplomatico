#!/bin/bash

# Script de Deploy para Boletim Diplomático
# Executa: ./deploy.sh

echo "🚀 Iniciando deploy do Boletim Diplomático..."

# Configurar projeto
PROJECT_ID="gen-lang-client-0413045052"
REGION="asia-south1"

echo "📋 Projeto: $PROJECT_ID"
echo "🌍 Região: $REGION"

# Build e deploy
echo "🔨 Executando build e deploy..."
gcloud builds submit --config cloudbuild.yaml . --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Deploy concluído com sucesso!"
    echo "🌐 URL do serviço: https://boletim-diplomatico-$PROJECT_ID.$REGION.run.app"
else
    echo "❌ Erro no deploy!"
    exit 1
fi 