"""
Theme classifier for documents using Gemini AI.
Tags documents with embassy priority themes.
"""
import json
import os
from typing import List, Dict
from app.logger import logger

VALID_TAGS = [
    'Agricultura',
    'Defesa',
    'Energia',
    'Ciência, Tecnologia e Inovação',
    'Saúde',
    'Comércio',
    'Cooperação Sul-Sul',
    'América Latina',
    'Brasil',
    'BRICS',
    'Política Externa',
    'Política Interna',
    'Economia',
    'Europa',
    'Ásia',
    'África',
    'América do Norte',
    'Oceania',
    'Oriente Médio',
]


def classify_all(docs: List[Dict]) -> None:
    """Classify all documents by theme using Gemini in a single batch call."""
    if not docs:
        return

    numbered = []
    for i, doc in enumerate(docs):
        title = doc.get('title', '')
        summary = doc.get('summary', '')
        numbered.append(f"{i}. {title} | {summary[:150]}")
    docs_block = '\n'.join(numbered)

    tags_list = ', '.join(VALID_TAGS)

    prompt = f"""Classifique cada documento abaixo com uma ou mais tags temáticas.

Tags disponíveis (use SOMENTE estas, exatamente como escritas):
{tags_list}

Regras:
- Atribua apenas tags realmente pertinentes ao conteúdo. Nem todo documento terá tags.
- "Brasil" = menciona Brasil, brasileiros ou relações com o Brasil.
- Responda SOMENTE com um JSON array, sem markdown, sem explicação.
- Formato: [{{"id": 0, "tags": ["Tag1", "Tag2"]}}, ...]

Documentos:
{docs_block}"""

    try:
        from google import genai
        from google.genai import types
        from app.config import GOOGLE_API_KEY

        client = genai.Client(api_key=GOOGLE_API_KEY)
        config = types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1]
            raw = raw.rsplit('```', 1)[0]
        results = json.loads(raw)

        for item in results:
            idx = item.get('id')
            tags = [t for t in item.get('tags', []) if t in VALID_TAGS]
            if 0 <= idx < len(docs):
                docs[idx]['tags'] = tags
                docs[idx]['brasil'] = 'Brasil' in tags

        # Ensure all docs have tags/brasil keys
        for doc in docs:
            doc.setdefault('tags', [])
            doc.setdefault('brasil', False)

        tagged = sum(1 for d in docs if d['tags'])
        logger.info(f"Classificação por IA: {tagged}/{len(docs)} documentos com tags")

    except Exception as e:
        logger.error(f"Erro na classificação por IA: {e}")
        # Fallback: set empty tags
        for doc in docs:
            doc.setdefault('tags', [])
            doc.setdefault('brasil', False)
