import requests
from app.config import (
    OLLAMA_API_URL, OLLAMA_MODEL,
    SUMMARIZER_PROVIDER, GOOGLE_API_KEY, GEMINI_MODEL
)
from app.logger import logger
import os
import re
from typing import List, Dict
from abc import ABC, abstractmethod


class BaseSummarizer(ABC):
    """Classe base abstrata para provedores de sumarização"""

    @abstractmethod
    def _call_api(self, prompt: str, system: str = None) -> str:
        """Chama a API do provedor para gerar texto"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifica se o provedor está disponível"""
        pass

    def _count_words(self, text: str) -> int:
        """Conta o número de palavras em um texto"""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)

    def _get_summarization_prompt(self, content: str) -> str:
        """Retorna o prompt padrão para sumarização"""
        return f"""Summarize the following official document in English. 

            CRITICAL: The summary MUST be between 50-60 words. Be concise and focus only on the most important diplomatic information.
            
            WORD COUNT REQUIREMENT:
            - Minimum: 50 words
            - Maximum: 60 words
            - Count your words and ensure the summary is within this range
            
            CONTENT GUIDELINES:
            - Focus on key diplomatic information and official positions
            - Use quotation marks for official statements, titles, or specific terminology
            - Be faithful to the original meaning
            - Prioritize: who, what, when and where of the diplomatic communication (but make the text fluid, no repetitive sentences)
            - Avoid starting every summary with the date (for example: "On March 4, 2026, ..."); vary the opening structure
            - Mention the exact date only when it is diplomatically relevant; otherwise focus on the actors and actions
            - Do not add interpretations or evaluations. Only restate the explicit content of the document in a neutral, factual tone.
            - Wrap only the person's name (not their title/role) in **double asterisks** (e.g. Prime Minister **Narendra Modi**, External Affairs Minister **S. Jaishankar**).
            
            STRICT LANGUAGE POLICY - CRITICAL:
            - The summary MUST be written ONLY in English
            - ABSOLUTELY NO Hindi, Malayalam, Tamil, Bengali, or any other Indian language text in the summary
            - If the document contains text in Indian languages, translate it completely to English
            - Do NOT include any Devanagari script, Tamil script, or any non-Latin characters
            - Do NOT include phrases like "भारत के संविधान" or any Hindi text - translate everything to English
            - Use ONLY English characters (A-Z, a-z, 0-9, and standard punctuation)
            - If translating from Indian languages, provide the English translation only - no original text
            - Use quotation marks for official statements, titles, or specific terminology in English only
            
            Document: {content[:4000]}
            
            Summary (50-60 words, ENGLISH ONLY - NO HINDI OR OTHER INDIAN LANGUAGES):"""

    def summarize_document(self, doc: Dict) -> str:
        """Sumariza um documento"""
        try:
            content = doc.get('content', '')
            if not content:
                return "Content not available for this document."

            # Debug: log content length
            logger.debug(f"Content para '{doc.get('title', 'Unknown')[:50]}': {len(content)} chars")

            prompt = self._get_summarization_prompt(content)
            response_text = self._call_api(prompt)

            if response_text:
                summary = response_text.strip()
                word_count = self._count_words(summary)
                logger.info(f"✅ Resumo gerado com {word_count} palavras")
                return summary
            else:
                logger.warning("Resposta vazia do provedor")
                return "Summary not available."
        except Exception as e:
            logger.error(f"Erro ao sumarizar documento: {e}")
            return f"Summary unavailable. Document title: {doc.get('title', 'Unknown')}"


class OllamaSummarizer(BaseSummarizer):
    """Provedor de sumarização usando Ollama (LLM local)"""

    def __init__(self):
        logger.info("Configurando Ollama API...")
        self.api_url = OLLAMA_API_URL or "http://localhost:11434/api/generate"
        self.model_name = OLLAMA_MODEL or "mistral"

        if not self.health_check():
            raise Exception("Ollama não está acessível")

        # Testar modelo
        try:
            test_response = self._call_api("Hello, respond with 'OK' if you can read this.")
            if test_response and "OK" in test_response.upper():
                logger.info(f"✅ Modelo {self.model_name} funcionando!")
            else:
                logger.warning(f"⚠️ Modelo retornou resposta inesperada")
        except Exception as e:
            logger.error(f"❌ Erro ao testar modelo {self.model_name}: {e}")
            raise Exception(f"Modelo {self.model_name} não está funcionando")

        logger.info(f"Ollama configurado com sucesso! Modelo: {self.model_name}")

    def health_check(self) -> bool:
        """Verifica se o Ollama está rodando"""
        try:
            health_url = self.api_url.replace("/api/generate", "/api/tags")
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Ollama está rodando em {self.api_url}")
                return True
            else:
                logger.warning(f"⚠️ Ollama retornou status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Não foi possível conectar ao Ollama em {self.api_url}")
            logger.error("💡 Certifique-se de que o Ollama está rodando: ollama serve")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar Ollama: {e}")
            return False

    def _call_api(self, prompt: str, system: str = None) -> str:
        """Chama a API do Ollama para gerar texto"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }

            if system:
                payload["system"] = system

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Erro na API do Ollama: {response.status_code} - {response.text[:200]}")
                return ""
        except requests.exceptions.Timeout:
            logger.error("Timeout ao chamar Ollama (mais de 2 minutos)")
            return ""
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {e}")
            return ""


class GeminiSummarizer(BaseSummarizer):
    """Provedor de sumarização usando Google Gemini (SDK google-genai)"""

    def __init__(self):
        logger.info("Configurando Google Gemini API...")

        if not GOOGLE_API_KEY:
            raise Exception("GOOGLE_API_KEY não configurada. Defina no arquivo .env")

        self.model_name = GEMINI_MODEL or "gemini-2.5-flash-preview-04-17"

        try:
            from google import genai
            from google.genai import types
            self._types = types
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
        except ImportError:
            raise Exception("Pacote google-genai não instalado. Execute: pip install google-genai")

        if not self.health_check():
            raise Exception("Gemini API não está acessível")

        logger.info(f"✅ Gemini configurado com sucesso! Modelo: {self.model_name}")

    def health_check(self) -> bool:
        """Verifica se a API do Gemini está acessível"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello, respond with 'OK' if you can read this.",
            )
            if response and getattr(response, "text", None) and "OK" in (response.text or "").upper():
                logger.info(f"✅ Gemini API funcionando com modelo {self.model_name}")
                return True
            else:
                logger.warning("⚠️ Gemini retornou resposta inesperada")
                return True  # Ainda pode funcionar
        except Exception as e:
            logger.error(f"❌ Erro ao verificar Gemini: {e}")
            return False

    def _call_api(self, prompt: str, system: str = None) -> str:
        """Chama a API do Gemini para gerar texto"""
        try:
            if system:
                full_prompt = f"{system}\n\n{prompt}"
            else:
                full_prompt = prompt

            config = self._types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=2048,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config,
            )

            raw_text = getattr(response, "text", None) if response else None
            if raw_text:
                logger.debug(f"Gemini raw response ({len(raw_text)} chars): {raw_text[:200]}...")
                return raw_text.strip()

            logger.warning("Resposta vazia do Gemini")
            return ""
        except Exception as e:
            logger.error(f"Erro ao chamar Gemini: {e}")
            return ""


class Summarizer:
    """
    Classe principal de sumarização que seleciona o provedor baseado na configuração.
    Mantém compatibilidade com a interface anterior.
    """

    def __init__(self):
        self.provider_name = SUMMARIZER_PROVIDER
        logger.info(f"Inicializando Summarizer com provedor: {self.provider_name}")

        if self.provider_name == 'gemini':
            self._provider = GeminiSummarizer()
        elif self.provider_name == 'ollama':
            self._provider = OllamaSummarizer()
        else:
            logger.warning(f"Provedor '{self.provider_name}' desconhecido. Usando Ollama como padrão.")
            self._provider = OllamaSummarizer()

        logger.info(f"✅ Summarizer inicializado com {self._provider.__class__.__name__}")

    def summarize_document(self, doc: Dict) -> str:
        """Sumariza um documento usando o provedor configurado"""
        return self._provider.summarize_document(doc)

    def compile_report(self, docs: List[Dict]) -> str:
        """Compila um relatório com todos os documentos sumarizados"""
        # Agrupar por tipo
        grouped = {}
        for doc in docs:
            tipo = doc['tipo']
            if tipo not in grouped:
                grouped[tipo] = []
            grouped[tipo].append(doc)

        logger.info(f"Documentos recebidos: {len(docs)}")
        logger.info(f"Tipos encontrados: {list(grouped.keys())}")
        for tipo, docs_list in grouped.items():
            logger.info(f"  {tipo}: {len(docs_list)} documentos")

        # Gerar sumários para todos os documentos
        for doc in docs:
            summary = self.summarize_document(doc)
            if summary is None:
                doc['summary'] = "Resumo não disponível devido a erro de processamento."
            else:
                doc['summary'] = summary

        # Montar saída simplificada
        output = []

        sections = [
            'Prime Minister Releases',
            'MEA - Press Releases',
            'MEA - Speeches & Statements',
            'MEA - Media Briefings'
        ]

        for section in sections:
            output.append(f"{section}")
            output.append("")

            if section in grouped and grouped[section]:
                for doc in grouped[section]:
                    date_str = doc['date'].strftime('%d/%m/%Y')
                    output.append(f"{date_str} - [{doc['title']}]({doc['link']})")
                    output.append(doc['summary'])
                    output.append("")
            else:
                output.append("Nenhum item publicado nesta seção desde o último boletim.")
                output.append("")

        return '\n'.join(output)

    def generate_daily_synthesis(self, docs: List[Dict], target_dates=None) -> str:
        """Generate a short narrative synthesis of the day in diplomatic Portuguese."""
        titles = [f"- {doc.get('title', '')}" for doc in docs]
        titles_block = '\n'.join(titles)

        # Determine date context for the prompt
        if target_dates and len(target_dates) > 1:
            dates_sorted = sorted(target_dates)
            date_context = f"no fim de semana de {dates_sorted[0].strftime('%d/%m')} e {dates_sorted[1].strftime('%d/%m')}"
        elif target_dates:
            date_context = f"no dia {target_dates[0].strftime('%d/%m/%Y')}"
        else:
            date_context = "ontem"

        prompt = f"""Com base nos títulos abaixo, que se referem a acontecimentos {date_context}, redija uma síntese dividida em duas partes. Use verbos no pretérito (aconteceu ontem, não hoje).

FORMATO OBRIGATÓRIO (use exatamente estas marcações):
[INTERNA]
2 a 3 frases sobre política interna: agenda do PM Modi, decisões de gabinete,
inaugurações, política doméstica. Se não houver conteúdo relevante, omita esta seção.

[EXTERNA]
2 a 3 frases sobre política externa: relações bilaterais, multilaterais, visitas,
declarações conjuntas, posicionamentos internacionais. Se não houver conteúdo relevante, omita esta seção.

FOCO: a agenda do Primeiro-Ministro Modi é sempre relevante.
Temas prioritários: agricultura, defesa, energia, ciência e tecnologia, comércio e saúde.

ESTILO: registro editorial de grande revista internacional (The Economist, Financial Times)
em português do Brasil.
- Resumo FACTUAL. Relate o que aconteceu, ponto. Não adicione interpretações genéricas
  como "o que sinaliza...", "em movimento que reflete...", "o que reforça o compromisso...".
  Esse tipo de análise rasa enche linguiça e não agrega informação.
- Análise SOMENTE quando for substantiva e puder ser extraída diretamente do conteúdo
  das notas — nunca como arremate vago de frase.
- Tom sóbrio e informado. Nunca irônico, nunca opinativo, nunca diplomaticamente
  sensível. O texto deve poder circular em ambiente diplomático sem causar embaraço.
- Frases curtas, com ritmo.
- REGRA GRAMATICAL INEGOCIÁVEL: não use gerúndio após vírgula. Em vez de
  ", reforçando", ", consolidando", ", ampliando" etc., reescreva com pretérito
  ("e reforçou"), presente ("o que reforça") ou oração subordinada ("ao reforçar").
  Revise o parágrafo inteiro antes de entregar e elimine qualquer ocorrência.
- Não mencione a Embaixada, o boletim nem o próprio texto.
- Coloque nomes próprios de pessoas em negrito usando **asteriscos duplos** (ex: **Narendra Modi**).
- Ao mencionar valores em rúpias, converta para dólares americanos (taxa aproximada: 1 USD = 85 INR).

Títulos do dia:
{titles_block}"""

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
            )
            synthesis = response.content[0].text.strip()
            logger.info(f"Síntese gerada via Claude ({len(synthesis)} chars): {synthesis[:100]}...")
            return synthesis
        except Exception as e:
            logger.error(f"Erro ao gerar síntese com Claude: {e}")
            # Fallback to configured provider
            response = self._provider._call_api(prompt)
            if response:
                return response.strip()
        return ""
