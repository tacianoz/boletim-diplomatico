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
        
        # Calcular período da Lok Sabha (semana anterior)
        loksabha_end = today - timedelta(days=1)  # Domingo
        loksabha_start = loksabha_end - timedelta(days=6)  # Segunda-feira
        
        # Formatar período da Lok Sabha
        if loksabha_start.month == loksabha_end.month:
            if loksabha_start.year == loksabha_end.year:
                loksabha_period = f"{loksabha_start.strftime('%d/%m/%Y')} a {loksabha_end.strftime('%d/%m/%Y')}"
            else:
                loksabha_period = f"{loksabha_start.strftime('%d/%m/%Y')} a {loksabha_end.strftime('%d/%m/%Y')}"
        else:
            loksabha_period = f"{loksabha_start.strftime('%d/%m/%Y')} a {loksabha_end.strftime('%d/%m/%Y')}"
        
        # Assunto do e-mail (dinâmico baseado nos PDFs gerados)
        if len(pdf_files) == 2:
            # Caso 1: Ambos os PDFs (boletim + loksabha) - Segunda-feira
            email_subject = f"Boletim Diplomático + Relatório Lok Sabha - {today.strftime('%d/%m/%Y')}"
            
            # Formatar período do boletim (sábado e domingo)
            if len(target_dates) == 2:
                boletim_period = f"{target_dates[0].strftime('%d/%m/%Y')} e {target_dates[1].strftime('%d/%m/%Y')}"
            else:
                boletim_period = target_dates[0].strftime('%d/%m/%Y')
            
            email_body = f"""Prezados/as colegas,

Segue em anexo:

1. Boletim Diplomático referente às publicações de {boletim_period}
2. Relatório Semanal Lok Sabha de {loksabha_period}

Atenciosamente,
Taciano S. Zimmermann"""
        else:
            # Caso 2: Apenas boletim (sem loksabha) - Segunda-feira
            email_subject = f"Boletim Diplomático - {today.strftime('%d/%m/%Y')}"
            
            # Formatar período do boletim (sábado e domingo)
            if len(target_dates) == 2:
                boletim_period = f"{target_dates[0].strftime('%d/%m/%Y')} e {target_dates[1].strftime('%d/%m/%Y')}"
            else:
                boletim_period = target_dates[0].strftime('%d/%m/%Y')
            
            email_body = f"""Prezados/as colegas,

Segue o Boletim Diplomático referente às publicações de {boletim_period}.

Nota: Não foram encontrados documentos da Lok Sabha para a semana anterior ({loksabha_period}).

Atenciosamente,
Taciano S. Zimmermann"""
        
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
