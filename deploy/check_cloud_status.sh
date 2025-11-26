#!/bin/bash

# Script para verificar o status do serviço no Google Cloud

PROJECT_ID="gen-lang-client-0413045052"
REGION="asia-south1"
SERVICE_NAME="notas-do-dia"

echo "🔍 Verificando status do serviço no Google Cloud..."
echo ""

# 1. Verificar status do serviço Cloud Run
echo "📊 Status do serviço Cloud Run:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="table(
        metadata.name,
        status.url,
        status.conditions[0].status,
        spec.template.spec.containers[0].image,
        status.latestReadyRevisionName,
        status.latestCreatedRevisionName
    )"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2. Verificar últimas revisões
echo "📋 Últimas revisões:"
gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --limit=5 \
    --format="table(
        metadata.name,
        status.conditions[0].status,
        spec.containers[0].image,
        metadata.creationTimestamp
    )"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. Verificar logs recentes (últimas 20 linhas)
echo "📝 Logs recentes (últimas 20 linhas):"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=20 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4. Verificar métricas de uso (últimas 24h)
echo "📈 Métricas de uso (últimas 24h):"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(status.traffic)"

echo ""
echo "✅ Verificação concluída!"

