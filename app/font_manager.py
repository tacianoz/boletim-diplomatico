#!/usr/bin/env python3
"""
Gerenciador de fontes Unicode para suporte a Hindi e outros caracteres
"""

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.logger import logger
import os

def register_unicode_fonts():
    """
    Registra fontes Unicode que suportam Hindi e outros caracteres especiais.
    Retorna as fontes disponíveis ou fallback para Helvetica.
    """
    
    # Lista de fontes Unicode para tentar (em ordem de preferência)
    font_paths = [
        # Linux - DejaVu (muito comum)
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans'),
        ('/usr/share/fonts/TTF/DejaVuSans.ttf', 'DejaVuSans'),
        ('/usr/share/fonts/dejavu/DejaVuSans.ttf', 'DejaVuSans'),
        
        # macOS - Arial Unicode MS
        ('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 'ArialUnicode'),
        ('/System/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode'),
        ('/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode'),
        
        # Windows - Arial Unicode MS (se rodando em WSL)
        ('/mnt/c/Windows/Fonts/arial.ttf', 'ArialUnicode'),
        ('/mnt/c/Windows/Fonts/ARIALUNI.TTF', 'ArialUnicode'),
        
        # Linux - Noto Sans (Google)
        ('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf', 'NotoSans'),
        ('/usr/share/fonts/noto/NotoSans-Regular.ttf', 'NotoSans'),
        
        # Linux - Liberation Sans
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans'),
        ('/usr/share/fonts/liberation/LiberationSans-Regular.ttf', 'LiberationSans'),
    ]
    
    bold_font_paths = [
        # Linux - DejaVu Bold
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        ('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        ('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        
        # macOS - Arial Unicode MS (mesmo arquivo para bold)
        ('/System/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode-Bold'),
        ('/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode-Bold'),
        
        # Windows - Arial Bold
        ('/mnt/c/Windows/Fonts/arialbd.ttf', 'ArialUnicode-Bold'),
        ('/mnt/c/Windows/Fonts/ARIALUNI.TTF', 'ArialUnicode-Bold'),
        
        # Linux - Noto Sans Bold
        ('/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf', 'NotoSans-Bold'),
        ('/usr/share/fonts/noto/NotoSans-Bold.ttf', 'NotoSans-Bold'),
        
        # Linux - Liberation Sans Bold
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 'LiberationSans-Bold'),
        ('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 'LiberationSans-Bold'),
    ]
    
    # Tentar registrar fonte normal
    unicode_font = 'Helvetica'  # Fallback padrão
    unicode_font_bold = 'Helvetica-Bold'  # Fallback padrão
    
    # Registrar fonte normal
    for font_path, font_name in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                unicode_font = font_name
                logger.info(f"✅ Fonte Unicode registrada: {font_name} ({font_path})")
                break
            except Exception as e:
                logger.warning(f"⚠️ Erro ao registrar fonte {font_path}: {e}")
                continue
    
    # Registrar fonte bold
    for font_path, font_name in bold_font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                unicode_font_bold = font_name
                logger.info(f"✅ Fonte Unicode Bold registrada: {font_name} ({font_path})")
                break
            except Exception as e:
                logger.warning(f"⚠️ Erro ao registrar fonte bold {font_path}: {e}")
                continue
    
    # Se não conseguiu registrar fontes Unicode, usar fallback
    if unicode_font == 'Helvetica':
        logger.warning("⚠️ Nenhuma fonte Unicode encontrada. Hindi pode aparecer como quadrados.")
    else:
        logger.info(f"✅ Fontes Unicode configuradas: {unicode_font} / {unicode_font_bold}")
    
    return unicode_font, unicode_font_bold

# Registrar fontes ao importar o módulo
UNICODE_FONT, UNICODE_FONT_BOLD = register_unicode_fonts() 