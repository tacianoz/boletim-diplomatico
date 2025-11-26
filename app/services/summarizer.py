import google.generativeai as genai
from app.config import GOOGLE_API_KEY
from app.logger import logger
import os
from typing import List, Dict

class Summarizer:
    def __init__(self):
        logger.info("Configurando Google Gemini API...")
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Lista de modelos para tentar em ordem de preferência
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-001',
            'gemini-2.5-flash',
            'gemini-1.5-flash-8b',
            'gemini-1.5-flash',
            'gemini-1.5-pro'
        ]
        
        self.model = None
        for model_name in models_to_try:
            try:
                logger.info(f"Tentando modelo: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                
                # Testar o modelo com uma requisição simples
                test_response = self.model.generate_content("test")
                if test_response and test_response.text:
                    logger.info(f"✅ Modelo {model_name} funcionando!")
                    break
                else:
                    logger.warning(f"Modelo {model_name} retornou resposta vazia")
                    self.model = None
            except Exception as e:
                logger.warning(f"Erro com modelo {model_name}: {e}")
                self.model = None
        
        if self.model is None:
            logger.error("❌ Nenhum modelo Gemini funcionando!")
            logger.warning("💡 Tentando Vertex AI como alternativa...")
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                
                # Configurar Vertex AI com o projeto do gcloud
                import subprocess
                result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                      capture_output=True, text=True)
                project_id = result.stdout.strip()
                logger.info(f"Usando projeto: {project_id}")
                # Tentar diferentes regiões para o Vertex AI
                regions_to_try = ["us-central1", "europe-west4", "asia-south1"]
                for region in regions_to_try:
                    try:
                        logger.info(f"Tentando região: {region}")
                        vertexai.init(project=project_id, location=region)
                        break
                    except Exception as e:
                        logger.warning(f"Erro com região {region}: {e}")
                        continue
                self.model = GenerativeModel("gemini-1.5-flash")
                
                # Testar o modelo Vertex AI
                test_response = self.model.generate_content("test")
                if test_response and test_response.text:
                    logger.info("✅ Vertex AI configurado com sucesso!")
                else:
                    logger.error("❌ Vertex AI retornou resposta vazia")
                    self.model = None
            except Exception as e:
                logger.error(f"❌ Vertex AI falhou: {e}")
                self.model = None
        
        if self.model is None:
            raise Exception("Nenhum modelo Gemini disponível")
        
        logger.info("Google Gemini configurado com sucesso!")

    def summarize_document(self, doc: Dict) -> str:
        try:
            # Verificar se o documento tem conteúdo
            content = doc.get('content', '')
            if not content:
                return "Content not available for this document."
            
            prompt = f"""Summarize the following official document in English. 
            CRITICAL: The summary MUST be between 50-60 words. Be concise and focus only on the most important diplomatic information.
            
            WORD COUNT REQUIREMENT:
            - Minimum: 50 words
            - Maximum: 60 words
            - Count your words and ensure the summary is within this range
            
            CONTENT GUIDELINES:
            - Focus on key diplomatic information and official positions
            - Use quotation marks for official statements, titles, or specific terminology
            - Be faithful to the original meaning
            - Prioritize: who, what, when, where, and why of the diplomatic communication
            
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
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                summary = response.text.strip()
                # Verificar e limpar qualquer texto em hindi ou outras línguas indianas
                summary = self._clean_summary(summary)
                return summary
            else:
                logger.warning("Resposta vazia do modelo")
                return "Summary not available."
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao sumarizar documento: {error_msg}")
            
            # Se for erro de API key expirada ou inválida, tentar reconfigurar
            if "API key" in error_msg.lower() or "API_KEY" in error_msg or "expired" in error_msg.lower():
                logger.warning("API key expirada ou inválida. Tentando reconfigurar...")
                try:
                    from app.config import GOOGLE_API_KEY
                    import google.generativeai as genai
                    genai.configure(api_key=GOOGLE_API_KEY)
                    # Tentar novamente com modelo mais simples
                    alt_model = genai.GenerativeModel('gemini-1.5-flash')
                    response = alt_model.generate_content(prompt)
                    if response and response.text:
                        logger.info("Sumarização bem-sucedida após reconfiguração")
                        return response.text.strip()
                except Exception as retry_e:
                    logger.error(f"Erro ao tentar reconfigurar: {retry_e}")
            
            # Se for erro 404 de modelo não encontrado, tentar modelo alternativo
            if "404" in error_msg and "model" in error_msg.lower():
                logger.warning("Tentando modelo alternativo devido a erro 404...")
                try:
                    # Tentar modelo alternativo
                    alt_model = genai.GenerativeModel('gemini-1.5-flash')
                    response = alt_model.generate_content(prompt)
                    if response and response.text:
                        logger.info("Sumarização bem-sucedida com modelo alternativo")
                        return response.text.strip()
                except Exception as alt_e:
                    logger.error(f"Erro também com modelo alternativo: {alt_e}")
            
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
