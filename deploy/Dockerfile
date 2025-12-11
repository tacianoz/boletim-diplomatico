FROM python:3.11-slim

# Detectar arquitetura e instalar dependências do sistema, Chrome e fontes Unicode
RUN ARCH=$(dpkg --print-architecture) && \
    apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    gnupg \
    unzip \
    xvfb \
    ca-certificates \
    curl \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2-data \
    && if [ "$ARCH" = "amd64" ]; then \
        # Chrome para amd64 (ChromeDriver será instalado via webdriver-manager)
        curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
        apt-get update && \
        apt-get install -y google-chrome-stable; \
    elif [ "$ARCH" = "arm64" ]; then \
        # Chrome para arm64 (usar Chromium como alternativa ou baixar Chrome para ARM)
        apt-get install -y chromium chromium-driver || \
        (wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
         echo "deb [arch=arm64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
         apt-get update && apt-get install -y google-chrome-stable || apt-get install -y chromium); \
    fi && \
    # Fontes Unicode
    apt-get install -y \
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

# Copiar código da aplicação (copiar arquivos Python primeiro para melhor cache)
COPY app/ ./app/
COPY generate_daily_notes.py ./
COPY app_web.py ./
COPY requirements.txt ./
# Copiar resto dos arquivos necessários
COPY *.py ./
COPY *.txt ./
COPY *.md ./

# Criar diretório para logs
RUN mkdir -p logs

# Configurar variáveis de ambiente para Chrome headless
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome

# Expor porta (se necessário para web)
EXPOSE 8080

# Variável de ambiente para porta
ENV PORT=8080

# Comando padrão - usar gunicorn se disponível, senão Flask
# Aumentar timeout para processos longos (scraping pode demorar)
CMD ["sh", "-c", "if command -v gunicorn > /dev/null; then gunicorn -w 2 -b 0.0.0.0:8080 --timeout 300 --graceful-timeout 30 app_web:app; else python app_web.py; fi"]
