#!/bin/bash
# Script para configurar cron job para Notas do Dia

# Obter caminho absoluto do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
SCRIPT="$PROJECT_DIR/generate_daily_notes.py"
LOG_DIR="$PROJECT_DIR/logs"

# Verificar se o virtual environment existe
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ ERRO: Virtual environment não encontrado em $PROJECT_DIR/venv"
    echo "Execute primeiro: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p "$LOG_DIR"

# Linha do cron (segunda a sábado às 6h)
CRON_LINE="0 6 * * 1-6 cd $PROJECT_DIR && $VENV_PYTHON $SCRIPT >> $LOG_DIR/cron.log 2>&1"

# Verificar se já existe no crontab
if crontab -l 2>/dev/null | grep -q "$SCRIPT"; then
    echo "⚠️  Já existe um job cron para este script."
    echo "Deseja substituir? (s/n)"
    read -r response
    if [ "$response" != "s" ]; then
        echo "Cancelado."
        exit 0
    fi
    # Remover linha antiga
    crontab -l 2>/dev/null | grep -v "$SCRIPT" | crontab -
fi

# Adicionar ao crontab
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo "✅ Cron job configurado com sucesso!"
echo ""
echo "📋 Job adicionado:"
echo "   $CRON_LINE"
echo ""
echo "📊 Para verificar: crontab -l"
echo "🗑️  Para remover: crontab -e (e deletar a linha)"

