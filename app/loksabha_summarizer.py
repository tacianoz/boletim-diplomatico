import google.generativeai as genai
from app.config import GOOGLE_API_KEY
from app.logger import logger
from typing import List, Dict

class LokSabhaSummarizer:
    def __init__(self):
        logger.info("Configurando Google Gemini API para Lok Sabha...")
        genai.configure(api_key=GOOGLE_API_KEY)
        # Usar Gemini 1.5 Flash (mais barato e rápido)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Google Gemini configurado com sucesso para Lok Sabha!")

    def summarize_question(self, question: Dict) -> str:
        """Sumariza uma question & answer específica"""
        try:
            prompt = f"""Summarize the following Lok Sabha Question & Answer in English. 
            Use 3-4 sentences for shorter documents and 4-5 sentences for longer, more complex documents.
            Focus on:
            1. The main question being asked
            2. The key points of the government's response
            3. Any important diplomatic or policy positions mentioned
            4. Specific data, numbers, or commitments if mentioned
            
            Be faithful to the original language and use quotation marks for official statements, 
            titles, or specific terminology. This is for diplomatic reporting purposes.
            
            LANGUAGE POLICY FOR FINAL SUMMARY:
            - Write the summary ONLY in English
            - Exceptionally, you may include very important phrases in Hindi if they are official statements or quotes
            - For any other languages (Malayalam, Tamil, Bengali, etc.), show ONLY the English translation with "tradução automática" note
            - Do NOT include original text in other languages in the final summary
            
            Examples:
            - Hindi (allowed): "सभी देशवासियों को जन्माष्टमी की असीम शुभकामनाएं।" (tradução automática: "Heartiest greetings to all countrymen on Janmashtami.")
            - Malayalam (not allowed in original): "Tributes to Mahatma Ayyankali on his Jayanti. He is remembered as an icon of social justice and empowerment." (tradução automática do malayalam)
            - Tamil (not allowed in original): "The government's commitment to inclusive development..." (tradução automática do tamil)
            
            Question & Answer Content: {question['content'][:4000]}
            
            Summary:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Erro ao sumarizar question: {e}")
            return "Error in summarization"

    def compile_weekly_report(self, questions: List[Dict]) -> str:
        """Compila o relatório semanal das questions & answers"""
        if not questions:
            return "Nenhuma question & answer encontrada para a semana anterior."
        
        # Gerar sumários para cada question
        for question in questions:
            question['summary'] = self.summarize_question(question)
        
        # Ordenar por data (mais recente primeiro)
        questions.sort(key=lambda x: x['date'], reverse=True)
        
        # Montar saída
        output = []
        
        # Cabeçalho
        output.append("Lok Sabha Questions & Answers - Weekly Summary")
        output.append("")  # Linha em branco
        
        # Período coberto
        dates = [q['date'] for q in questions]
        start_date = min(dates)
        end_date = max(dates)
        output.append(f"Period: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}")
        output.append("")  # Linha em branco
        
        # Questions organizadas por data
        current_date = None
        for question in questions:
            # Adicionar separador de data se mudou
            if current_date != question['date']:
                current_date = question['date']
                output.append(f"=== {current_date.strftime('%A, %d %B %Y')} ===")
                output.append("")  # Linha em branco
            
            # Formato: [Título com link]
            output.append(f"[{question['title']}]({question['link']})")
            output.append(question['summary'])
            output.append("")  # Linha em branco entre questions
        
        return '\n'.join(output)
