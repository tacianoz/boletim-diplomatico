FROM python:3.11-slim

# Instalar dependências do sistema, Chrome e fontes Unicode completas
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    gnupg \
    unzip \
    xvfb \
    # Chrome e ChromeDriver
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    # Fontes Unicode
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

# Configurar variáveis de ambiente para Chrome headless
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome

# Expor porta (se necessário para web)
EXPOSE 8080

# Comando padrão
CMD ["python", "app_web.py"]
