# Deploy do Boletim Diplomático

## 🚀 Deploy no Google Cloud Run

### **Pré-requisitos**
- Google Cloud SDK instalado e configurado
- Projeto ativo no Google Cloud
- APIs habilitadas: Cloud Run, Container Registry

### **Configuração do Projeto**
```bash
# Definir projeto ativo
gcloud config set project SEU_PROJETO_ID

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### **Build e Deploy Automático**
```bash
# Deploy usando Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

### **Deploy Manual**
```bash
# 1. Build da imagem
docker build -t gcr.io/SEU_PROJETO_ID/boletim-diplomatico .

# 2. Push para Container Registry
docker push gcr.io/SEU_PROJETO_ID/boletim-diplomatico

# 3. Deploy no Cloud Run
gcloud run deploy boletim-diplomatico \
  --image gcr.io/SEU_PROJETO_ID/boletim-diplomatico \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 1 \
  --set-env-vars TIMEZONE=Asia/Kolkata
```

## 🐳 Docker Local

### **Build da Imagem**
```bash
docker build -t boletim-diplomatico .
```

### **Execução Local**
```bash
# Executar container
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=sua_chave \
  -e EMAIL_USER=seu_email \
  -e EMAIL_PASS=sua_senha \
  boletim-diplomatico

# Executar com volume para logs
docker run -p 8080:8080 \
  -v $(pwd)/logs:/app/logs \
  -e GOOGLE_API_KEY=sua_chave \
  -e EMAIL_USER=seu_email \
  -e EMAIL_PASS=sua_senha \
  boletim-diplomatico
```

## ⚙️ Variáveis de Ambiente

### **Obrigatórias**
```bash
GOOGLE_API_KEY=sua_chave_do_google_ai_studio
EMAIL_USER=seu_email_gmail
EMAIL_PASS=sua_senha_app_gmail
```

### **Opcionais**
```bash
TIMEZONE=Asia/Kolkata  # Padrão: Asia/Kolkata
LOG_LEVEL=INFO         # Padrão: INFO
```

## 🔧 Configurações do Selenium

### **Chrome Headless**
- O Docker inclui Chrome e ChromeDriver
- Configurado para execução headless
- Variáveis de ambiente configuradas automaticamente

### **Recursos Necessários**
- **Memória:** 4Gi (aumentado para suportar Chrome)
- **CPU:** 2 cores
- **Timeout:** 3600s (1 hora)

## 📊 Monitoramento

### **Logs do Cloud Run**
```bash
# Ver logs em tempo real
gcloud logs tail --service=boletim-diplomatico

# Ver logs específicos
gcloud logs read --service=boletim-diplomatico --limit=50
```

### **Métricas**
- Cloud Run fornece métricas automáticas
- Monitorar uso de memória e CPU
- Verificar latência das requisições

## 🚨 Troubleshooting

### **Problemas Comuns**

#### **1. Erro de Memória**
```bash
# Aumentar memória no Cloud Run
gcloud run services update boletim-diplomatico \
  --memory 6Gi \
  --region asia-south1
```

#### **2. Timeout do Selenium**
```bash
# Aumentar timeout
gcloud run services update boletim-diplomatico \
  --timeout 7200 \
  --region asia-south1
```

#### **3. Problemas com Chrome**
```bash
# Verificar logs do container
docker logs CONTAINER_ID

# Executar com debug
docker run -e DEBUG=1 boletim-diplomatico
```

## 📈 Escalabilidade

### **Configurações Recomendadas**
- **Desenvolvimento:** 2Gi RAM, 1 CPU
- **Produção:** 4Gi RAM, 2 CPU
- **Alto tráfego:** 6Gi RAM, 4 CPU

### **Auto-scaling**
- Cloud Run gerencia automaticamente
- Configurar `--max-instances` conforme necessidade
- Monitorar custos e performance

---

**Última atualização:** Setembro 2025

