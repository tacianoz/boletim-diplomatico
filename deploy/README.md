# Arquivos de Deploy

Esta pasta contém todos os arquivos relacionados ao deploy do projeto no Google Cloud Run.

## 📁 Arquivos

### `deploy.sh`
Script principal de deploy. Executa:
- Build da imagem Docker
- Push para Google Container Registry
- Deploy no Cloud Run

**Uso:**
```bash
cd deploy
./deploy.sh
```

### `cloudbuild.yaml`
Configuração do Google Cloud Build para deploy automatizado.

**Uso:**
```bash
gcloud builds submit --config deploy/cloudbuild.yaml
```

### `check_cloud_status.sh`
Script para verificar o status do serviço no Google Cloud Run.

**Uso:**
```bash
cd deploy
./check_cloud_status.sh
```

### `DEPLOY.md`
Documentação completa sobre o processo de deploy, incluindo:
- Pré-requisitos
- Configuração
- Deploy manual e automatizado
- Troubleshooting
- Monitoramento

## ⚙️ Configuração

Antes de usar os scripts, configure o `PROJECT_ID` no arquivo `deploy.sh`:

```bash
PROJECT_ID="seu-projeto-id-aqui"
```

## 📝 Notas

- O `Dockerfile` está na pasta `deploy/` mas os scripts fazem build a partir da raiz do projeto
- Os scripts assumem que você está executando a partir da raiz do projeto ou da pasta `deploy/`
- Certifique-se de ter o `gcloud` CLI instalado e autenticado

