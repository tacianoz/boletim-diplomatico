import requests
from app.config import OLLAMA_API_URL, OLLAMA_MODEL
from app.logger import logger
import os
from typing import List, Dict

class Summarizer:
    def __init__(self):
        logger.info("Configurando Ollama API...")
        
        # Configuração padrão do Ollama
        self.api_url = OLLAMA_API_URL or "http://localhost:11434/api/generate"
        self.model_name = OLLAMA_MODEL or "mistral"
        
        # Verificar se o Ollama está rodando
        try:
            health_url = self.api_url.replace("/api/generate", "/api/tags")
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Ollama está rodando em {self.api_url}")
            else:
                logger.warning(f"⚠️ Ollama retornou status {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Não foi possível conectar ao Ollama em {self.api_url}")
            logger.error("💡 Certifique-se de que o Ollama está rodando: ollama serve")
            raise Exception("Ollama não está acessível")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar Ollama: {e}")
        
        # Testar o modelo com uma requisição simples
        try:
            test_prompt = "Hello, respond with 'OK' if you can read this."
            test_response = self._call_ollama(test_prompt)
            if test_response and "OK" in test_response.upper():
                logger.info(f"✅ Modelo {self.model_name} funcionando!")
            else:
                logger.warning(f"⚠️ Modelo {self.model_name} retornou resposta inesperada: {test_response[:50]}")
        except Exception as e:
            logger.error(f"❌ Erro ao testar modelo {self.model_name}: {e}")
            raise Exception(f"Modelo {self.model_name} não está funcionando")
        
        logger.info(f"Ollama configurado com sucesso! Modelo: {self.model_name}")
    
    def _call_ollama(self, prompt: str, system: str = None) -> str:
        """
        Chama a API do Ollama para gerar texto
        """
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
                timeout=120  # Timeout de 2 minutos para respostas longas
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

    def _count_words(self, text: str) -> int:
        """Conta o número de palavras em um texto"""
        import re
        # Remove pontuação e conta palavras
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)
    
    def _truncate_summary(self, summary: str, max_words: int = 60) -> str:
        """Trunca o resumo para no máximo max_words palavras de forma inteligente"""
        import re
        # Contar palavras corretamente
        words = re.findall(r'\b\w+\b', summary)
        word_count = len(words)
        
        if word_count <= max_words:
            return summary
        
        # Tentar truncar por sentenças primeiro (mais natural)
        sentences = re.split(r'([.!?]\s+)', summary)
        result_sentences = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = re.findall(r'\b\w+\b', sentence)
            sentence_word_count = len(sentence_words)
            
            if current_word_count + sentence_word_count <= max_words:
                result_sentences.append(sentence)
                current_word_count += sentence_word_count
            else:
                # Não cabe mais uma sentença completa
                # Se ainda temos espaço para pelo menos 5 palavras, pegar algumas palavras
                remaining = max_words - current_word_count
                if remaining >= 5:
                    # Pegar palavras individuais da próxima sentença
                    all_words_in_sentence = re.findall(r'\S+', sentence)
                    partial_sentence = ' '.join(all_words_in_sentence[:remaining])
                    result_sentences.append(partial_sentence)
                break
        
        truncated_text = ''.join(result_sentences).strip()
        
        # Validação final: garantir que não ultrapasse
        final_words = re.findall(r'\b\w+\b', truncated_text)
        if len(final_words) > max_words:
            # Fallback: truncamento direto por palavras
            all_tokens = re.findall(r'\S+', summary)
            truncated_text = ' '.join(all_tokens[:max_words])
            # Remover pontuação final estranha
            truncated_text = truncated_text.rstrip('.,;:')
        
        # Contar palavras finais (extrair para variável para evitar backslash em f-string)
        final_word_count = len(re.findall(r'\b\w+\b', truncated_text))
        logger.info(f"Resumo truncado de {word_count} para {final_word_count} palavras")
        return truncated_text
    
    def _refine_summary(self, summary: str, original_content: str) -> str:
        """Refina o resumo se estiver fora do limite de palavras"""
        word_count = self._count_words(summary)
        
        if word_count < 50:
            # Se tiver menos de 50 palavras, tentar expandir um pouco
            logger.warning(f"Resumo com apenas {word_count} palavras. Tentando expandir...")
            expansion_prompt = f"""The following summary is too short ({word_count} words). Expand it to exactly 50-60 words by adding more key diplomatic details from the original document.

Original document excerpt: {original_content[:2000]}

Current summary: {summary}

Expanded summary (exactly 50-60 words, English only):"""
            
            expanded = self._call_ollama(expansion_prompt)
            if expanded and self._count_words(expanded) >= 50:
                return expanded.strip()
        
        elif word_count > 60:
            # Se tiver mais de 60 palavras, truncar
            logger.warning(f"Resumo com {word_count} palavras (excede limite de 60). Truncando...")
            return self._truncate_summary(summary, 60)
        
        # Se estiver entre 50-60 palavras, retornar como está
        return summary
    
    def summarize_document(self, doc: Dict) -> str:
        try:
            # Verificar se o documento tem conteúdo
            content = doc.get('content', '')
            if not content:
                return "Content not available for this document."
            
            prompt = f"""Summarize the following official document in English. 
CRITICAL: The summary MUST be EXACTLY 50-60 words. Count your words carefully and ensure the summary is within this range.

WORD COUNT REQUIREMENT - STRICT:
- Minimum: 50 words (no less)
- Maximum: 60 words (no more)
- You MUST count words and ensure the summary is within this exact range
- Stop when you reach 60 words maximum

CONTENT GUIDELINES:
- Focus on key diplomatic information and official positions
- Use quotation marks for official statements, titles, or specific terminology
- Be faithful to the original meaning
- Prioritize: who, what, when, where, and why of the diplomatic communication (but make the text fluid, no repetitive sentences)

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

Summary (EXACTLY 50-60 words, ENGLISH ONLY - NO HINDI OR OTHER INDIAN LANGUAGES):"""
            
            response_text = self._call_ollama(prompt)
            if response_text:
                summary = response_text.strip()
                # Verificar e limpar qualquer texto em hindi ou outras línguas indianas
                summary = self._clean_summary(summary)
                
                # Validar e ajustar contagem de palavras
                word_count = self._count_words(summary)
                logger.info(f"Resumo gerado com {word_count} palavras")
                
                # VALIDAÇÃO RIGOROSA: Garantir que está entre 50-60 palavras
                if word_count < 50:
                    # Tentar expandir se estiver muito curto
                    summary = self._refine_summary(summary, content)
                    word_count = self._count_words(summary)
                    logger.info(f"Resumo após refinamento: {word_count} palavras")
                
                if word_count > 60:
                    # TRUNCAR se exceder 60 palavras (garantia final)
                    logger.warning(f"⚠️ Resumo com {word_count} palavras excede limite. Truncando para 60 palavras.")
                    summary = self._truncate_summary(summary, 60)
                    final_word_count = self._count_words(summary)
                    logger.info(f"✅ Resumo truncado para {final_word_count} palavras")
                
                # Validação final: garantir que nunca ultrapasse 60
                final_check = self._count_words(summary)
                if final_check > 60:
                    # Última linha de defesa: truncamento direto
                    logger.warning(f"⚠️ Validação final: ainda com {final_check} palavras. Aplicando truncamento direto.")
                    all_tokens = summary.split()
                    summary = ' '.join(all_tokens[:60])
                
                final_word_count = self._count_words(summary)
                if final_word_count < 50:
                    logger.warning(f"⚠️ Resumo final com apenas {final_word_count} palavras (mínimo: 50)")
                
                logger.info(f"✅ Resumo final: {final_word_count} palavras")
                return summary
            else:
                logger.warning("Resposta vazia do Ollama")
                return "Summary not available."
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao sumarizar documento: {error_msg}")
            
            # Retornar mensagem de erro mais informativa
            logger.warning(f"Retornando resumo genérico devido a erro: {error_msg[:100]}")
            return f"Summary unavailable. Document title: {doc.get('title', 'Unknown')}"
    
    def _clean_summary(self, summary: str) -> str:
        """
        Remove any Hindi, Tamil, Bengali, or other Indian language text from summary.
        Keeps only English text.
        """
        import re
        
        # Ranges Unicode para scripts indianos comuns
        # Devanagari (Hindi, Marathi, etc.): U+0900-U+097F
        # Tamil: U+0B80-U+0BFF
        # Bengali: U+0980-U+09FF
        # Telugu: U+0C00-U+0C7F
        # Malayalam: U+0D00-U+0D7F
        # Gujarati: U+0A80-U+0AFF
        # Kannada: U+0C80-U+0CFF
        # Oriya: U+0B00-U+0B7F
        # Punjabi: U+0A00-U+0A7F
        
        indian_script_pattern = re.compile(
            r'[\u0900-\u097F\u0B80-\u0BFF\u0980-\u09FF\u0C00-\u0C7F\u0D00-\u0D7F'
            r'\u0A80-\u0AFF\u0C80-\u0CFF\u0B00-\u0B7F\u0A00-\u0A7F]+'
        )
        
        # Remover qualquer texto em scripts indianos
        cleaned = indian_script_pattern.sub('', summary)
        
        # Limpar espaços extras que possam ter ficado
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Se o resumo foi completamente removido (só tinha hindi), retornar mensagem padrão
        if not cleaned or len(cleaned) < 10:
            logger.warning("Resumo continha apenas texto em hindi/outras línguas indianas. Retornando mensagem padrão.")
            return "Summary contains content in Indian languages. English translation not available."
        
        # Verificar se ainda há caracteres problemáticos
        if indian_script_pattern.search(cleaned):
            logger.warning("Ainda há caracteres indianos no resumo após limpeza. Removendo novamente...")
            cleaned = indian_script_pattern.sub('', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    def compile_report(self, docs: List[Dict]) -> str:
        # Agrupar por tipo
        grouped = {}
        for doc in docs:
            tipo = doc['tipo']
            if tipo not in grouped:
                grouped[tipo] = []
            grouped[tipo].append(doc)
        
        # Debug: verificar o agrupamento
        logger.info(f"Documentos recebidos: {len(docs)}")
        logger.info(f"Tipos encontrados: {list(grouped.keys())}")
        for tipo, docs_list in grouped.items():
            logger.info(f"  {tipo}: {len(docs_list)} documentos")
        
        # Debug: verificar estrutura dos primeiros documentos
        if docs:
            logger.info(f"Primeiro documento - tipo: '{docs[0].get('tipo', 'SEM_TIPO')}', título: {docs[0].get('title', 'SEM_TITULO')[:50]}...")
            if len(docs) > 1:
                logger.info(f"Segundo documento - tipo: '{docs[1].get('tipo', 'SEM_TIPO')}', título: {docs[1].get('title', 'SEM_TITULO')[:50]}...")
        
        # Debug: verificar todos os tipos dos documentos
        tipos_unicos = set(doc.get('tipo', 'SEM_TIPO') for doc in docs)
        logger.info(f"Todos os tipos únicos encontrados: {tipos_unicos}")
        
        # Debug: verificar se há documentos com tipo 'Prime Minister Releases'
        pm_docs = [doc for doc in docs if doc.get('tipo') == 'Prime Minister Releases']
        logger.info(f"Documentos com tipo 'Prime Minister Releases': {len(pm_docs)}")
        if pm_docs:
            logger.info(f"Primeiro documento PM: {pm_docs[0].get('title', 'SEM_TITULO')[:50]}...")
        
        # Gerar sumários para todos os documentos
        for doc in docs:
            summary = self.summarize_document(doc)
            if summary is None:
                # Se a sumarização falhou, usar uma mensagem padrão
                doc['summary'] = "Resumo não disponível devido a erro de processamento."
            else:
                doc['summary'] = summary
        
        # Montar saída simplificada
        output = []
        
        # Ordem específica das seções
        sections = [
            'Prime Minister Releases', 
            'MEA - Press Releases', 
            'MEA - Speeches & Statements', 
            'MEA - Media Briefings'
        ]
        
        for section in sections:
            output.append(f"{section}")
            output.append("")  # Linha em branco
            
            if section in grouped and grouped[section]:
                for doc in grouped[section]:
                    # Formato: Data - [Título com link]
                    date_str = doc['date'].strftime('%d/%m/%Y')
                    output.append(f"{date_str} - [{doc['title']}]({doc['link']})")
                    output.append(doc['summary'])
                    output.append("")  # Linha em branco entre documentos
            else:
                # Adicionar mensagem quando não há documentos
                output.append("Nenhum item publicado nesta seção desde o último boletim.")
                output.append("")  # Linha em branco
        
        return '\n'.join(output)
