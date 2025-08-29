FROM python:3.11-slim

# Instalar dependências do sistema e fontes Unicode completas
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-noto \
    fonts-noto-core \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-liberation \
    fonts-liberation2 \
    fonts-indic \
    fonts-beng \
    fonts-deva \
    fonts-gujr \
    fonts-guru \
    fonts-knda \
    fonts-mlym \
    fonts-orya \
    fonts-taml \
    fonts-telu \
    fonts-lao \
    fonts-thai-tlwg \
    fonts-tibetan-machine \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    fonts-ipafont-gothic \
    fonts-ipafont-mincho \
    fonts-unfonts-core \
    fonts-unfonts-extra \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para cache
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p logs

# Expor porta (se necessário para web)
EXPOSE 8080

# Comando padrão
CMD ["python", "app_web.py"]
