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
            IMPORTANT: Use EXACTLY 2-3 sentences for the summary.
            ONLY use 4-5 sentences for exceptionally long documents (over 2000 words).
            
            Be faithful to the original language and use quotation marks for official statements, 
            titles, or specific terminology. Focus on the key diplomatic information and official positions.
            
            LANGUAGE POLICY FOR FINAL SUMMARY:
            - Write the summary ONLY in English
            - For any text in Hindi, Malayalam, Tamil, Bengali, or other Indian languages, provide ONLY the English translation
            - Do NOT include original text in any Indian language in the final summary
            - If translating from Indian languages, add "(translated from [language])" note
            - Use quotation marks for official statements, titles, or specific terminology in English only
            
            Examples:
            - Hindi text should become: "Heartiest greetings to all countrymen on Janmashtami." (translated from Hindi)
            - Malayalam text should become: "Tributes to Mahatma Ayyankali on his Jayanti. He is remembered as an icon of social justice and empowerment." (translated from Malayalam)
            - Tamil text should become: "The government's commitment to inclusive development..." (translated from Tamil)
            
            Document: {content[:4000]}
            
            Summary:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao sumarizar documento: {error_msg}")
            
            # Se for erro 404 de modelo não encontrado, tentar modelo alternativo
            if "404" in error_msg and "model" in error_msg.lower():
                logger.warning("Tentando modelo alternativo devido a erro 404...")
                try:
                    # Tentar modelo alternativo
                    alt_model = genai.GenerativeModel('gemini-1.5-pro')
                    response = alt_model.generate_content(prompt)
                    logger.info("Sumarização bem-sucedida com modelo alternativo")
                    return response.text.strip()
                except Exception as alt_e:
                    logger.error(f"Erro também com modelo alternativo: {alt_e}")
            
            # Retornar mensagem de erro para indicar falha na sumarização
            return "Error in summarization"

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
        
        # Gerar sumários para documentos regulares
        for doc in docs:
            if not doc['tipo'].startswith('UN '):
                summary = self.summarize_document(doc)
                if summary is None:
                    # Se a sumarização falhou, usar uma mensagem padrão
                    doc['summary'] = "Resumo não disponível devido a erro de processamento."
                else:
                    doc['summary'] = summary
        
        # Processar statements da ONU separadamente
        un_statements = []
        for doc in docs:
            if doc['tipo'].startswith('UN '):
                un_statements.append(doc)
        
        # Sumarizar statements da ONU se houver
        if un_statements:
            try:
                from app.un_statements_summarizer import UNStatementsSummarizer
                un_summarizer = UNStatementsSummarizer()
                un_summary = un_summarizer.summarize_statements(un_statements)
                
                # Adicionar resumo aos statements individuais
                for statement in un_statements:
                    statement['summary'] = un_summary
            except Exception as e:
                logger.error(f"Erro ao sumarizar statements da ONU: {e}")
                for statement in un_statements:
                    statement['summary'] = "Erro ao processar statement da ONU."
        
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
        
        # Adicionar seção de UN Statements no final
        if un_statements:
            output.append("UN Statements")
            output.append("")  # Linha em branco
            
            # Ordenar statements por data (mais recente primeiro)
            un_statements.sort(key=lambda x: x['date'], reverse=True)
            
            for statement in un_statements:
                # Formato: data - UNGA/UNSC - título com link
                date_str = statement['date'].strftime('%d/%m/%Y')
                org = "UNSC" if "Security Council" in statement['tipo'] else "UNGA"
                output.append(f"{date_str} - {org} - [{statement['title']}]({statement['link']})")
                
                # quem proferiu
                speaker = statement.get('speaker', '').replace('Statement by ', '')
                if speaker:
                    output.append(f"SPEAKER: {speaker}")
                
                # resumo
                output.append(statement['summary'])
                output.append("")  # Linha em branco entre statements
        else:
            output.append("UN Statements")
            output.append("")  # Linha em branco
            output.append("Nenhum item publicado nesta seção desde o último boletim.")
            output.append("")  # Linha em branco
        
        return '\n'.join(output)
