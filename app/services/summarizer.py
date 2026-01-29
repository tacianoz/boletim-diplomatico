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
        return f"""You are a diplomatic analyst. Write a complete summary of this official government document.

REQUIREMENTS:
1. Write exactly 40-50 words - no less, no more
2. Write in English only
3. Include: WHO was involved, WHAT happened, WHEN, WHERE, and WHY it matters
4. End with a complete sentence (never cut off mid-sentence)
5. Focus on key diplomatic points and official positions

DOCUMENT TO SUMMARIZE:
{content[:4000]}

Write your 40-50 word summary now (complete sentences only):"""

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
    """Provedor de sumarização usando Google Gemini"""

    def __init__(self):
        logger.info("Configurando Google Gemini API...")

        if not GOOGLE_API_KEY:
            raise Exception("GOOGLE_API_KEY não configurada. Defina no arquivo .env")

        self.model_name = GEMINI_MODEL or "gemini-2.5-flash-preview-04-17"

        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(self.model_name)
            self.genai = genai
        except ImportError:
            raise Exception("Pacote google-generativeai não instalado. Execute: pip install google-generativeai")

        if not self.health_check():
            raise Exception("Gemini API não está acessível")

        logger.info(f"✅ Gemini configurado com sucesso! Modelo: {self.model_name}")

    def health_check(self) -> bool:
        """Verifica se a API do Gemini está acessível"""
        try:
            response = self.model.generate_content("Hello, respond with 'OK' if you can read this.")
            if response and response.text and "OK" in response.text.upper():
                logger.info(f"✅ Gemini API funcionando com modelo {self.model_name}")
                return True
            else:
                logger.warning(f"⚠️ Gemini retornou resposta inesperada")
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

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 2048,
            }

            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            if response:
                # Log response details
                if response.candidates:
                    candidate = response.candidates[0]
                    finish_reason = candidate.finish_reason
                    if str(finish_reason) != "FinishReason.STOP" and str(finish_reason) != "1":
                        logger.warning(f"⚠️ Gemini finish_reason: {finish_reason}")

            if response and response.text:
                raw_text = response.text
                logger.debug(f"Gemini raw response ({len(raw_text)} chars): {raw_text[:200]}...")
                return raw_text.strip()
            elif response and response.candidates:
                # Tentar extrair texto dos candidates
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        text = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                        if text:
                            return text.strip()

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
