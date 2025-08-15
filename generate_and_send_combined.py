#!/usr/bin/env python3
"""
Script para gerar ambos os PDFs (Boletim Diplomático e Lok Sabha) e enviar no mesmo e-mail
"""

from generate_pdf import create_pdf_boletim
from generate_loksabha_pdf import create_loksabha_pdf
from app.emailer import send_email
from app.logger import logger
from datetime import datetime
import os

def generate_and_send_combined():
    """Gera ambos os PDFs e envia no mesmo e-mail"""
    logger.info("=== GERANDO E ENVIANDO PDFs COMBINADOS ===")
    
    try:
        pdf_files = []
        
        # 1. Gerar PDF do Boletim Diplomático
        logger.info("1. Gerando PDF do Boletim Diplomático...")
        boletim_pdf = create_pdf_boletim()
        if boletim_pdf:
            pdf_files.append(boletim_pdf)
            logger.info(f"✅ PDF do Boletim gerado: {boletim_pdf}")
        else:
            logger.error("❌ Erro ao gerar PDF do Boletim")
            return False
        
        # 2. Gerar PDF da Lok Sabha
        logger.info("2. Gerando PDF da Lok Sabha...")
        loksabha_pdf = create_loksabha_pdf()
        if loksabha_pdf:
            pdf_files.append(loksabha_pdf)
            logger.info(f"✅ PDF da Lok Sabha gerado: {loksabha_pdf}")
        else:
            logger.info("ℹ️ Nenhum documento da Lok Sabha encontrado para a semana anterior")
            logger.info("ℹ️ Enviando apenas o Boletim Diplomático")
            # Não retorna False, apenas continua sem o PDF da Lok Sabha
        
        # 3. Preparar e-mail
        today = datetime.now().date()
        
        # Calcular período da Lok Sabha para o e-mail
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        month_names = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        start_day = last_monday.day
        end_day = last_sunday.day
        month = month_names[last_monday.month]
        year = last_monday.year
        
        if start_day == end_day:
            loksabha_period = f"{start_day} de {month} de {year}"
        else:
            loksabha_period = f"{start_day} a {end_day} de {month} de {year}"
        
        # Assunto do e-mail (dinâmico baseado nos PDFs gerados)
        if len(pdf_files) == 2:
            email_subject = f"Boletim Diplomático + Relatório Lok Sabha - {today.strftime('%d/%m/%Y')}"
            email_body = f"""Prezados/as colegas,

Segue em anexo:

1. Boletim Diplomático de {today.strftime('%d/%m/%Y')} (resumo dos comunicados, discursos e briefings do MEA)
2. Relatório Semanal Lok Sabha de {loksabha_period} (resumo das questions & answers da Lok Sabha ao MEA)

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi"""
        else:
            email_subject = f"Boletim Diplomático - {today.strftime('%d/%m/%Y')}"
            email_body = f"""Prezados/as colegas,

Segue o Boletim Diplomático de {today.strftime('%d/%m/%Y')}.

Nota: Não foram encontrados documentos da Lok Sabha para a semana anterior ({loksabha_period}).

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi"""
        
        # 4. Enviar e-mail com ambos os PDFs
        logger.info("3. Enviando e-mail com ambos os PDFs...")
        
        send_email(
            subject=email_subject,
            body=email_body,
            attachments=pdf_files
        )
        
        logger.info("✅ E-mail enviado com sucesso!")
        print("✅ E-mail enviado com sucesso!")
        print(f"📧 Assunto: {email_subject}")
        print(f"📎 Anexos: {len(pdf_files)} PDFs")
        for pdf in pdf_files:
            print(f"   - {pdf}")
        
        if len(pdf_files) == 1:
            print("ℹ️ Apenas o Boletim Diplomático foi enviado (sem documentos da Lok Sabha)")
        else:
            print("✅ Ambos os relatórios foram enviados")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar e enviar PDFs combinados: {e}")
        print(f"❌ Erro ao gerar e enviar PDFs combinados: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from datetime import timedelta
    
    success = generate_and_send_combined()
    if success:
        print("\n🎉 Processo concluído com sucesso!")
        print("📧 PDFs foram gerados e enviados conforme disponibilidade")
    else:
        print("\n❌ Erro no processo. Verifique os logs.")
