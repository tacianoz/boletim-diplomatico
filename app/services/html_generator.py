"""
HTML Email Generator for Notas do Dia - India
Colors matched to Embaixada do Brasil logo:
  Navy:   #1C2443
  Green:  #2E9E3E
  Yellow: #E8C72C
  Blue:   #3B4DA0
"""
from datetime import datetime
from typing import List, Dict
from app.logger import logger
from xml.sax.saxutils import escape
import re


MONTH_NAMES = {
    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
}

SECTIONS = [
    'Prime Minister Releases',
    'MEA - Press Releases',
    'MEA - Speeches & Statements',
    'MEA - Media Briefings',
]

THEME_COLORS = {
    'Agricultura': '#4a7c3f',
    'Defesa': '#8b3a3a',
    'Energia': '#c27a1e',
    'Ciência, Tecnologia e Inovação': '#3B4DA0',
    'Saúde': '#2a7d6e',
    'Comércio': '#6b5b3e',
    'Cooperação Sul-Sul': '#6a4c93',
    'América Latina': '#2E9E3E',
    'Brasil': '#2E9E3E',
    'BRICS': '#c27a1e',
    'Política Externa': '#5a5a8a',
    'Política Interna': '#7a5a6a',
    'Economia': '#7a6530',
    'Europa': '#2a5a9b',
    'Ásia': '#8b5e3c',
    'África': '#6b8a3e',
    'América do Norte': '#4a6e8a',
    'Oceania': '#3a8a8a',
    'Oriente Médio': '#9a6b3a',
}


class HTMLGenerator:
    """Generates HTML email body with Brazilian Embassy theme"""

    def generate(self, docs: List[Dict], target_dates=None, synthesis: str = None) -> str:
        logger.info("=== GERANDO HTML DO NOTAS DO DIA ===")

        grouped: Dict[str, List[Dict]] = {}
        for doc in docs:
            grouped.setdefault(doc['tipo'], []).append(doc)

        if target_dates and len(target_dates) > 1:
            dates_sorted = sorted(target_dates)
            parts = [f"{d.day} de {MONTH_NAMES[d.month]} de {d.year}" for d in dates_sorted]
            date_str = " e ".join(parts)
        elif target_dates:
            d = target_dates[0]
            date_str = f"{d.day} de {MONTH_NAMES[d.month]} de {d.year}"
        else:
            today = datetime.now().date()
            date_str = f"{today.day} de {MONTH_NAMES[today.month]} de {today.year}"

        sections_html = self._build_sections(grouped)
        synthesis_html = self._build_synthesis(synthesis) if synthesis else ""

        html = f"""\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Notas do dia</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f5f7;font-family:Georgia,'Times New Roman',Times,serif;-webkit-font-smoothing:antialiased;">

<!--[if mso]><style>table,td {{font-family:Arial,sans-serif !important;}}</style><![endif]-->

<!-- Hidden preheader -->
<div style="display:none;font-size:1px;color:#f4f5f7;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">
  Resumo di&aacute;rio de notas &agrave; imprensa do governo indiano &mdash; {escape(date_str)}
</div>

<!-- Container -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f5f7;">
<tr><td align="center" style="padding:40px 16px;">

<!-- Card -->
<table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">

<!-- Navy header with logo left + title right -->
<tr><td style="background-color:#1C2443;padding:0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <!-- Logo -->
    <td width="148" style="padding:18px 0 18px 28px;vertical-align:middle;">
      <img src="cid:logo" alt="Embaixada do Brasil" width="130" height="130" style="display:block;border:0;border-radius:8px;">
    </td>
    <!-- Title + subtitle -->
    <td style="padding:16px 28px 16px 20px;vertical-align:middle;">
      <p style="margin:0;font-size:28px;font-weight:400;color:#ffffff;line-height:1.2;font-family:Georgia,'Times New Roman',Times,serif;">
        Notas do dia
      </p>
      <p style="margin:8px 0 0 0;font-size:15px;color:rgba(255,255,255,0.6);font-family:Helvetica,Arial,sans-serif;line-height:1.4;">
        Resumo di&aacute;rio de notas &agrave; imprensa do governo indiano
      </p>
    </td>
  </tr>
  </table>
</td></tr>

<!-- Tri-color bar -->
<tr><td style="font-size:0;line-height:0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="33.33%" style="height:4px;background-color:#2E9E3E;">&nbsp;</td>
    <td width="33.34%" style="height:4px;background-color:#E8C72C;">&nbsp;</td>
    <td width="33.33%" style="height:4px;background-color:#3B4DA0;">&nbsp;</td>
  </tr></table>
</td></tr>

<!-- Date bar -->
<tr><td style="padding:12px 40px;background-color:#f9f9fb;">
  <p style="margin:0;font-size:15px;color:#1C2443;font-family:Helvetica,Arial,sans-serif;font-weight:600;">
    {escape(date_str)}
  </p>
</td></tr>

<!-- Synthesis -->
{synthesis_html}

<!-- Sections -->
{sections_html}

<!-- Footer -->
<tr><td style="padding:32px 40px;background-color:#f9f9fb;border-top:1px solid #eeeff2;">
  <p style="margin:0;font-size:13px;color:#9198a5;font-family:Helvetica,Arial,sans-serif;line-height:1.8;text-align:center;">
    Embaixada do Brasil &mdash; Nova D&eacute;lhi, &Iacute;ndia<br>
    Boletim gerado automaticamente com base em publica&ccedil;&otilde;es oficiais do governo indiano.
  </p>
</td></tr>

<!-- Bottom tri-color bar -->
<tr><td style="font-size:0;line-height:0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="33.33%" style="height:4px;background-color:#2E9E3E;">&nbsp;</td>
    <td width="33.34%" style="height:4px;background-color:#E8C72C;">&nbsp;</td>
    <td width="33.33%" style="height:4px;background-color:#3B4DA0;">&nbsp;</td>
  </tr></table>
</td></tr>

</table>
<!-- /Card -->

</td></tr>
</table>
<!-- /Container -->

</body>
</html>"""

        logger.info("HTML gerado com sucesso")
        return html

    def _build_synthesis(self, synthesis: str) -> str:
        sections = self._parse_synthesis_sections(synthesis)
        blocks = []
        for label, text in sections:
            formatted = self._format_bold(text.strip())
            blocks.append(f"""\
    <p style="margin:{'16px' if blocks else '0'} 0 4px 0;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#1C2443;font-family:Helvetica,Arial,sans-serif;font-weight:700;">
      {escape(label)}
    </p>
    <p style="margin:0;font-size:15px;line-height:1.8;color:#3d4050;font-family:Georgia,'Times New Roman',Times,serif;">
      {formatted}
    </p>""")
        content = '\n'.join(blocks)

        return f"""\
<tr><td style="padding:28px 40px 0 40px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="padding:20px 24px;background-color:#fdf8e8;border-radius:6px;border-left:3px solid #E8C72C;">
    <p style="margin:0 0 12px 0;font-size:11px;letter-spacing:2.5px;text-transform:uppercase;color:#E8C72C;font-family:Helvetica,Arial,sans-serif;font-weight:700;">
      S&iacute;ntese do dia
    </p>
{content}
  </td></tr>
  </table>
</td></tr>"""

    def _parse_synthesis_sections(self, synthesis: str):
        """Parse [INTERNA] and [EXTERNA] sections from synthesis text."""
        sections = []
        current_label = None
        current_text = []

        for line in synthesis.split('\n'):
            stripped = line.strip()
            if stripped == '[INTERNA]':
                if current_label and current_text:
                    sections.append((current_label, ' '.join(current_text)))
                current_label = 'Pol\u00edtica Interna'
                current_text = []
            elif stripped == '[EXTERNA]':
                if current_label and current_text:
                    sections.append((current_label, ' '.join(current_text)))
                current_label = 'Pol\u00edtica Externa'
                current_text = []
            elif stripped:
                if current_label:
                    current_text.append(stripped)
                else:
                    # No section marker — treat as single block
                    current_label = 'S\u00edntese'
                    current_text.append(stripped)

        if current_label and current_text:
            sections.append((current_label, ' '.join(current_text)))

        # Fallback: if no sections parsed, return whole text
        if not sections:
            sections.append(('S\u00edntese', synthesis))

        return sections

    def _format_bold(self, text: str) -> str:
        """Escape HTML but preserve **bold** markdown as <b> tags."""
        escaped = escape(text)
        return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escaped)

    def _build_sections(self, grouped: Dict[str, List[Dict]]) -> str:
        parts = []
        for section in SECTIONS:
            docs = grouped.get(section, [])
            parts.append(self._build_section(section, docs))
        return '\n'.join(parts)

    def _build_section(self, title: str, docs: List[Dict]) -> str:
        count = len(docs)
        count_badge = f' ({count})' if count else ''

        if docs:
            items_html = '\n'.join(self._build_item(doc) for doc in docs)
        else:
            items_html = f"""\
<tr><td style="padding:0 40px 0 40px;">
  <p style="margin:0;font-size:15px;color:#b0b4be;font-style:italic;font-family:Helvetica,Arial,sans-serif;">
    Nenhum item publicado nesta se&ccedil;&atilde;o desde o &uacute;ltimo boletim.
  </p>
</td></tr>"""

        return f"""\
<!-- Section: {escape(title)} -->
<tr><td style="padding:30px 40px 0 40px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="border-bottom:2px solid #E8C72C;padding-bottom:10px;">
      <h2 style="margin:0;font-size:13px;letter-spacing:2.5px;text-transform:uppercase;color:#2E9E3E;font-family:Helvetica,Arial,sans-serif;font-weight:700;">
        {escape(title)}<span style="color:#9198a5;font-weight:400;">{count_badge}</span>
      </h2>
    </td>
  </tr>
  </table>
</td></tr>

<tr><td style="padding:18px 0 0 0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  {items_html}
  </table>
</td></tr>"""

    def _build_item(self, doc: Dict) -> str:
        title = escape(doc.get('title', ''))
        link = escape(doc.get('link', ''))
        summary = self._format_bold(doc.get('summary', ''))
        date_str = doc['date'].strftime('%d/%m/%Y')
        is_brasil = doc.get('brasil', False)
        tags = doc.get('tags', [])

        # Brasil highlight: green left border + flag
        if is_brasil:
            border_color = '#2E9E3E'
            brasil_badge = '<span style="display:inline-block;background-color:#2E9E3E;color:#ffffff;font-size:10px;font-family:Helvetica,Arial,sans-serif;font-weight:700;padding:2px 6px;border-radius:3px;letter-spacing:0.5px;margin-left:6px;vertical-align:middle;">BRASIL</span>'
        else:
            border_color = '#1C2443'
            brasil_badge = ''

        # Theme tags
        tags_html = ''
        if tags:
            tag_spans = []
            for tag in tags:
                if tag == 'Brasil':
                    continue  # Already shown as badge
                color = THEME_COLORS.get(tag, '#6b7080')
                tag_spans.append(
                    f'<span style="display:inline-block;font-size:10px;font-family:Helvetica,Arial,sans-serif;'
                    f'color:{color};border:1px solid {color};padding:1px 6px;border-radius:3px;'
                    f'margin-right:4px;margin-top:4px;letter-spacing:0.3px;text-transform:lowercase;">{escape(tag)}</span>'
                )
            if tag_spans:
                tags_html = f'<p style="margin:8px 0 0 0;">{"".join(tag_spans)}</p>'

        return f"""\
<tr><td style="padding:0 40px 22px 40px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="padding:16px 20px;background-color:#fafbfc;border-radius:6px;border-left:3px solid {border_color};">
    <p style="margin:0 0 4px 0;font-size:13px;color:#9198a5;font-family:Helvetica,Arial,sans-serif;">
      {date_str}
    </p>
    <p style="margin:0 0 10px 0;font-size:18px;line-height:1.4;font-family:Georgia,'Times New Roman',Times,serif;">
      <a href="{link}" style="color:#1C2443;text-decoration:none;" target="_blank">
        {title}
      </a>{brasil_badge}
    </p>
    <p style="margin:0;font-size:16px;line-height:1.75;color:#4d5163;font-family:Georgia,'Times New Roman',Times,serif;">
      {summary}
    </p>
    {tags_html}
  </td></tr>
  </table>
</td></tr>"""
