import google.generativeai as genai
from app.config import GOOGLE_API_KEY
from app.logger import logger
import os
from typing import List, Dict

class Summarizer:
    def __init__(self):
        logger.info("Configurando Google Gemini API...")
        genai.configure(api_key=GOOGLE_API_KEY)
        # Usar Gemini 1.5 Flash (mais barato e rápido)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Google Gemini configurado com sucesso!")

    def summarize_document(self, doc: Dict) -> str:
        try:
            prompt = f"""Summarize the following official document in 2-3 sentences in English. 
            Be faithful to the original language and use quotation marks for official statements, 
            titles, or specific terminology. Focus on the key diplomatic information and official positions.
            
            Document: {doc['content'][:4000]}
            
            Summary:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Erro ao sumarizar documento: {e}")
            return "Error in summarization"

    def compile_report(self, docs: List[Dict]) -> str:
        # Agrupar por tipo
        grouped = {}
        for doc in docs:
            tipo = doc['tipo']
            if tipo not in grouped:
                grouped[tipo] = []
            grouped[tipo].append(doc)
        
        # Gerar sumários
        for doc in docs:
            doc['summary'] = self.summarize_document(doc)
        
        # Montar saída simplificada
        output = []
        
        # Ordem específica das seções
        sections = ['Prime Minister Releases', 'MEA - Press Releases', 'MEA - Speeches & Statements', 'MEA - Media Briefings']
        
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
                output.append("Nenhum item publicado ontem nesta seção.")
                output.append("")  # Linha em branco
        
        return '\n'.join(output)
