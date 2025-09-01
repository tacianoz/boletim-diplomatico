import google.generativeai as genai
from typing import List, Dict
from app.logger import logger
from app.config import GOOGLE_API_KEY
import os

class UNStatementsSummarizer:
    def __init__(self):
        api_key = GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não configurada")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def summarize_statements(self, statements: List[Dict]) -> str:
        """Sumariza uma lista de statements da ONU"""
        if not statements:
            return "Nenhum statement da ONU encontrado para o período."
        
        # Preparar texto para sumarização
        statements_text = self._prepare_statements_text(statements)
        
        # Prompt para sumarização
        prompt = f"""
        Você é um especialista em diplomacia e relações internacionais. Analise os seguintes statements da Índia na ONU (General Assembly e Security Council) e crie um resumo conciso e informativo.

        Statements:
        {statements_text}

        Instruções:
        1. Crie um resumo de 2-3 frases para cada statement
        2. Mantenha apenas inglês
        3. Foque nos pontos principais e posições da Índia
        4. Use linguagem diplomática e profissional
        5. NÃO adicione comentários sobre quantidade de statements
        6. Apenas forneça o resumo direto

        Formato do resumo:
        [RESUMO DIRETO DO STATEMENT]
        """
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            if not summary:
                return "Erro ao gerar resumo dos statements da ONU."
            
            logger.info(f"Resumo gerado para {len(statements)} statements da ONU")
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao sumarizar statements da ONU: {e}")
            return f"Erro ao processar statements da ONU: {str(e)}"
    
    def _prepare_statements_text(self, statements: List[Dict]) -> str:
        """Prepara o texto dos statements para sumarização"""
        text_parts = []
        
        for statement in statements:
            # Ordenar por data (mais recente primeiro)
            statements.sort(key=lambda x: x['date'], reverse=True)
        
        for statement in statements:
            text_part = f"""
            Data: {statement['date']}
            Tipo: {statement['tipo']}
            Título: {statement['title']}
            Speaker: {statement['speaker']}
            URL: {statement['link']}
            """
            
            if statement.get('content'):
                text_part += f"Conteúdo: {statement['content'][:1000]}...\n"
            
            text_parts.append(text_part)
        
        return "\n---\n".join(text_parts)
    
    def get_statements_summary_for_pdf(self, statements: List[Dict]) -> str:
        """Gera um resumo formatado para inclusão no PDF"""
        if not statements:
            return "Nenhum statement da ONU encontrado para o período."
        
        # Ordenar por data (mais recente primeiro)
        statements.sort(key=lambda x: x['date'], reverse=True)
        
        summary_lines = []
        summary_lines.append("STATEMENTS DA ONU")
        summary_lines.append("=" * 50)
        
        for statement in statements:
            date_str = statement['date'].strftime("%d/%m/%Y")
            tipo = statement['tipo']
            title = statement['title']
            speaker = statement['speaker']
            
            summary_lines.append(f"\n{date_str} - {tipo}")
            summary_lines.append(f"Título: {title}")
            if speaker:
                summary_lines.append(f"Speaker: {speaker}")
            summary_lines.append("-" * 30)
        
        return "\n".join(summary_lines)
