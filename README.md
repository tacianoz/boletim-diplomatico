# Boletim Diplomático + Lok Sabha – Scraper e Resumidor Automático

Este app Python faz scraping diário de comunicados, discursos e briefings do Ministério de Relações Exteriores da Índia, além de um relatório semanal das questions & answers da Lok Sabha, resume com Google Gemini AI e gera PDFs elegantes para envio automático por e-mail.

## 🚀 Funcionalidades

### 📰 **Boletim Diplomático Diário**
- Scraping robusto de quatro seções oficiais da Índia:
  - **Prime Minister Releases** (PIB) - com suporte a frames/iframes
  - **MEA Press Releases** - comunicados oficiais
  - **MEA Speeches & Statements** - discursos e declarações
  - **MEA Media Briefings** - briefings para a imprensa
- Processamento inteligente de datas (segunda-feira pega sábado e domingo)
- Múltiplos seletores para máxima compatibilidade
- Tratamento de erros e retry automático
- Suporte especial para conteúdo em frames (Prime Minister)

### 🏛️ **Relatório Semanal Lok Sabha**
- Scraping semanal das questions & answers da Lok Sabha ao MEA
- Busca questions da semana anterior (segunda a domingo)
- Resumos específicos focados em posições diplomáticas e políticas
- Execução automática toda segunda-feira às 7h
- PDF separado com formato similar ao boletim diplomático

### 🤖 **IA e Processamento**
- Sumarização com Google Gemini 1.5 Flash
- Extração de temas e informações diplomáticas
- Processamento em inglês com resumos concisos
- Tratamento de documentos longos
- Prompts específicos para questions & answers da Lok Sabha

### 📄 **Geração de PDF**
- Layout profissional com fundo azul claro
- Fonte Helvetica moderna e legível
- Cores sóbrias adequadas para documentos diplomáticos
- Bordas elegantes no cabeçalho e título
- Espaçamento otimizado e hierarquia visual clara
- **Dois PDFs separados:** Boletim Diplomático e Relatório Lok Sabha

### 📧 **Sistema de E-mail**
- Envio automático via Gmail SMTP
- Anexos PDF automáticos
- Texto profissional personalizado
- Suporte a múltiplos destinatários
- E-mails separados para cada tipo de relatório

### ⏰ **Agendamento Inteligente**
- **Segunda-feira às 6h:** Boletim Diplomático (sábado e domingo) + Relatório Lok Sabha (semana anterior)
- **Terça a Sábado às 6h:** Apenas Boletim Diplomático (dia anterior)
- Domingo excluído (sem execução)
- Lógica de datas otimizada para fins de semana
- Logging completo de execução

## 📁 Estrutura do Projeto

```
boletim-diplomatico/
├── app/
│   ├── __init__.py              # Pacote principal
│   ├── config.py                # Configurações e variáveis de ambiente
│   ├── scraper.py               # Scraping do boletim diplomático
│   ├── loksabha_scraper.py      # Scraping específico da Lok Sabha
│   ├── summarizer.py            # Sumarização do boletim diplomático
│   ├── loksabha_summarizer.py   # Sumarização específica da Lok Sabha
│   ├── emailer.py               # Sistema de envio de e-mails
│   ├── scheduler.py             # Agendamento do boletim diplomático
│   ├── loksabha_scheduler.py    # Agendamento específico da Lok Sabha
│   └── logger.py                # Sistema de logs
├── generate_pdf.py              # Geração de PDF do boletim diplomático
├── generate_loksabha_pdf.py     # Geração de PDF da Lok Sabha
├── main.py                      # Execução do boletim diplomático
├── loksabha_main.py             # Execução da Lok Sabha
├── combined_main.py             # Execução combinada de ambos
├── test_email.py                # Script de teste completo
├── requirements.txt             # Dependências Python
├── env.example                  # Exemplo de configuração
└── README.md                    # Esta documentação
```

## ⚙️ Configuração

### 1. **Clone o repositório**
```bash
git clone https://github.com/tacianoz/boletim-diplomatico.git
cd boletim-diplomatico
```

### 2. **Configure o ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

### 4. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite o arquivo .env com suas credenciais
```

### 5. **Configure o Google Gemini**
- Obtenha uma API key em [Google AI Studio](https://makersuite.google.com/app/apikey)
- Adicione a chave no arquivo `.env`:
  ```
  GOOGLE_API_KEY=sua_chave_aqui
  ```

### 6. **Configure o Gmail**
- Ative autenticação de 2 fatores no Gmail
- Gere uma senha de app em [myaccount.google.com](https://myaccount.google.com)
- Configure no `.env`:
  ```
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_USER=seu_email@gmail.com
  EMAIL_PASSWORD=sua_senha_de_app
  EMAIL_FROM=seu_email@gmail.com
  EMAIL_TO=destinatario@dominio.com
  ```

## 🚀 Execução

### **Execução Manual**
```bash
python generate_pdf.py                  # Gera PDF do boletim diplomático
python generate_loksabha_pdf.py         # Gera PDF da Lok Sabha
python generate_and_send_combined.py    # Gera ambos os PDFs e envia no mesmo e-mail
python test_pdfs.py                     # Testa geração de ambos os PDFs
python test_combined_pdfs.py            # Testa sistema combinado completo
```

### **Execução Automática**
```bash
python main.py                      # Apenas boletim diplomático
python loksabha_main.py             # Apenas relatório Lok Sabha (agendamento separado às 7h)
python combined_main.py             # Ambos os serviços (recomendado - segunda 6h: ambos, terça-sábado 6h: apenas boletim)
```

### **Agendamento**
- **Segunda-feira às 6h:** Boletim Diplomático (sábado e domingo) + Relatório Lok Sabha (semana anterior)
- **Terça a Sábado às 6h:** Apenas Boletim Diplomático (dia anterior)
- **Domingo:** Não executa automaticamente

## 📊 Logs e Monitoramento

- **Logs principais:** `logs/boletim.log`
- **Rotação:** Semanal com retenção de 4 semanas
- **Níveis:** INFO, ERROR, DEBUG
- **Formato:** Timestamp + nível + módulo + mensagem

## 🎨 Características dos PDFs

### **Layout Profissional**
- Fundo azul claro elegante (`#f0f4f8`)
- Fonte Helvetica moderna
- Cores sóbrias para contexto diplomático
- Bordas sutis no cabeçalho e título

### **Boletim Diplomático**
- **Título:** "Boletim Diplomático"
- **Conteúdo:** Resumos diários de notas à imprensa, discursos, comunicados e media briefings
- **Organização:** Por seções (Press Releases, Speeches, Media Briefings)

### **Relatório Lok Sabha**
- **Título:** "Relatório Semanal - Lok Sabha"
- **Conteúdo:** Resumos semanais das questions & answers da Lok Sabha ao MEA
- **Organização:** Por data, com separadores de dia da semana
- **Foco:** Posições diplomáticas e políticas do governo indiano

## 🔧 Tecnologias Utilizadas

- **Python 3.8+**
- **BeautifulSoup4** - Scraping HTML
- **Google Gemini API** - Sumarização com IA
- **ReportLab** - Geração de PDFs
- **APScheduler** - Agendamento de tarefas
- **SMTP** - Envio de e-mails
- **Loguru** - Sistema de logs

## 📝 Exemplos de E-mail

### **Boletim Diplomático**
```
Prezados/as colegas,

Segue o Boletim Diplomático de 07/08/2025.

Atenciosamente,
Taciano S. Zimmermann
```

### **Relatório Combinado (Segunda-feira)**
```
Prezados/as colegas,

Segue em anexo:

1. Boletim Diplomático de 12/08/2025 (resumo dos comunicados, discursos e briefings do MEA)
2. Relatório Semanal Lok Sabha de 05/08/2025 a 11/08/2025 (resumo das questions & answers da Lok Sabha ao MEA)

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi
```

## 🛠️ Desenvolvimento

### **Estrutura de Dados - Boletim Diplomático**
```python
document = {
    'tipo': 'Press Releases',
    'title': 'Título do documento',
    'link': 'https://www.mea.gov.in/...',
    'date': datetime.date(2025, 8, 6),
    'content': 'Conteúdo completo do documento',
    'summary': 'Resumo gerado pela IA'
}
```

### **Estrutura de Dados - Lok Sabha**
```python
question = {
    'title': 'QUESTION NO - 292 RELATION WITH WEST ASIAN COUNTRIES',
    'link': 'https://www.mea.gov.in/lok-sabha.htm?dtl/39984/...',
    'date': datetime.date(2025, 8, 8),
    'content': 'Conteúdo completo da question & answer',
    'summary': 'Resumo gerado pela IA'
}
```

### **Testes**
```bash
python test_pdfs.py          # Teste de geração de PDFs
python test_loksabha_only.py # Teste específico da Lok Sabha (recomendado)
python test_loksabha.py      # Teste completo da funcionalidade Lok Sabha
python test_combined.py      # Teste combinado de ambas as funcionalidades
```

## 📄 Licença

Este projeto é desenvolvido para uso interno da Embaixada do Brasil em Nova Délhi.

## 🤝 Contribuição

Para contribuições, entre em contato com a equipe de desenvolvimento.

## 📞 Contato

**Desenvolvido por:** Taciano S. Zimmermann  
**Instituição:** Embaixada do Brasil em Nova Délhi  
**Repositório:** https://github.com/tacianoz/boletim-diplomatico 