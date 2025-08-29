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
        
        # Linux - Noto Sans (Google) - mais completo para Hindi
        ('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf', 'NotoSans'),
        ('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
        
        # Linux - Liberation Sans
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans'),
        
        # macOS - Arial Unicode MS
        ('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 'ArialUnicode'),
        ('/System/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode'),
        ('/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode'),
        
        # Windows - Arial Unicode MS (se rodando em WSL)
        ('/mnt/c/Windows/Fonts/arial.ttf', 'ArialUnicode'),
        ('/mnt/c/Windows/Fonts/ARIALUNI.TTF', 'ArialUnicode'),
    ]
    
    bold_font_paths = [
        # Linux - DejaVu Bold
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        ('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        ('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        
        # macOS - Arial Bold (suporta Unicode)
        ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'ArialBold'),
        # macOS - Arial Unicode MS (mesmo arquivo para bold)
        ('/System/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode-Bold'),
        ('/Library/Fonts/Arial Unicode MS.ttf', 'ArialUnicode-Bold'),
        
        # Windows - Arial Bold
        ('/mnt/c/Windows/Fonts/arialbd.ttf', 'ArialUnicode-Bold'),
        ('/mnt/c/Windows/Fonts/ARIALUNI.TTF', 'ArialUnicode-Bold'),
        
        # Linux - Noto Sans Bold
        ('/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf', 'NotoSans-Bold'),
        
        # Linux - Liberation Sans Bold
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 'LiberationSans-Bold'),
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
        # Para Hindi, usar sempre a fonte Unicode normal
        unicode_font_bold = unicode_font
        logger.info(f"✅ Fontes Unicode configuradas: {unicode_font} / {unicode_font_bold}")
    
    return unicode_font, unicode_font_bold

# Registrar fontes ao importar o módulo
UNICODE_FONT, UNICODE_FONT_BOLD = register_unicode_fonts()

def contains_unicode_chars(text):
    """
    Detecta se o texto contém caracteres Unicode (Hindi, Tamil, Malayalam, etc.)
    """
    if not text:
        return False
    
    # Verificar se há caracteres de scripts não-latinos
    for char in text:
        code_point = ord(char)
        
        # Hindi (Devanagari): 0x0900-0x097F
        # Bengali: 0x0980-0x09FF
        # Tamil: 0x0B80-0x0BFF
        # Telugu: 0x0C00-0x0C7F
        # Malayalam: 0x0D00-0x0D7F
        # Gujarati: 0x0A80-0x0AFF
        # Kannada: 0x0C80-0x0CFF
        # Oriya: 0x0B00-0x0B7F
        # Punjabi: 0x0A00-0x0A7F
        
        if (0x0900 <= code_point <= 0x097F or  # Hindi
            0x0980 <= code_point <= 0x09FF or  # Bengali
            0x0B80 <= code_point <= 0x0BFF or  # Tamil
            0x0C00 <= code_point <= 0x0C7F or  # Telugu
            0x0D00 <= code_point <= 0x0D7F or  # Malayalam
            0x0A80 <= code_point <= 0x0AFF or  # Gujarati
            0x0C80 <= code_point <= 0x0CFF or  # Kannada
            0x0B00 <= code_point <= 0x0B7F or  # Oriya
            0x0A00 <= code_point <= 0x0A7F):   # Punjabi
            return True
    return False

def get_appropriate_font(text, is_bold=False):
    """
    Retorna a fonte apropriada baseada no conteúdo do texto
    """
    if contains_unicode_chars(text):
        # Se tem caracteres Unicode (Hindi), usar fonte Unicode normal
        return UNICODE_FONT
    else:
        # Se é texto ASCII (inglês), usar fonte apropriada
        if is_bold:
            return 'Helvetica-Bold'  # Inglês em negrito
        else:
            return 'Helvetica'  # Inglês normal 