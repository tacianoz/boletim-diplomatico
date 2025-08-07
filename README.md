# Boletim Diplomático – Scraper e Resumidor Automático

Este app Python faz scraping diário de comunicados, discursos e briefings do Ministério de Relações Exteriores da Índia, resume com Google Gemini AI e gera PDFs elegantes para envio automático por e-mail.

## 🚀 Funcionalidades

### 📰 **Scraping Inteligente**
- Scraping robusto de três seções do site do MEA Índia
- Processamento inteligente de datas (segunda-feira pega sábado e domingo)
- Múltiplos seletores para máxima compatibilidade
- Tratamento de erros e retry automático

### 🤖 **IA e Processamento**
- Sumarização com Google Gemini 1.5 Flash
- Extração de temas e informações diplomáticas
- Processamento em inglês com resumos concisos
- Tratamento de documentos longos

### 📄 **Geração de PDF**
- Layout profissional com fundo azul claro
- Fonte Helvetica moderna e legível
- Cores sóbrias adequadas para documentos diplomáticos
- Bordas elegantes no cabeçalho e título
- Espaçamento otimizado e hierarquia visual clara

### 📧 **Sistema de E-mail**
- Envio automático via Gmail SMTP
- Anexos PDF automáticos
- Texto profissional personalizado
- Suporte a múltiplos destinatários

### ⏰ **Agendamento Inteligente**
- Execução automática segunda a sábado às 8h
- Domingo excluído (sem execução)
- Lógica de datas otimizada para fins de semana
- Logging completo de execução

## 📁 Estrutura do Projeto

```
boletim_diplomatico/
├── app/
│   ├── __init__.py          # Pacote principal
│   ├── config.py            # Configurações e variáveis de ambiente
│   ├── scraper.py           # Scraping robusto do MEA Índia
│   ├── summarizer.py        # Sumarização com Google Gemini
│   ├── emailer.py           # Sistema de envio de e-mails
│   ├── scheduler.py         # Agendamento inteligente
│   └── logger.py            # Sistema de logs
├── generate_pdf.py          # Geração de PDFs elegantes
├── test_email.py            # Script de teste completo
├── main.py                  # Execução principal
├── requirements.txt         # Dependências Python
├── env.example              # Exemplo de configuração
└── README.md               # Esta documentação
```

## ⚙️ Configuração

### 1. **Clone o repositório**
```bash
git clone https://github.com/tacianoz/boletim-diplomatico.git
cd boletim_diplomatico
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
python generate_pdf.py    # Gera apenas o PDF
python test_email.py      # Gera PDF e envia por e-mail
```

### **Execução Automática**
```bash
python main.py            # Inicia o agendamento automático
```

### **Agendamento**
- **Segunda-feira:** 8h - Busca documentos de sábado e domingo
- **Terça a Sábado:** 8h - Busca documentos do dia anterior
- **Domingo:** Não executa automaticamente

## 📊 Logs e Monitoramento

- **Logs principais:** `logs/boletim.log`
- **Rotação:** Semanal com retenção de 4 semanas
- **Níveis:** INFO, ERROR, DEBUG
- **Formato:** Timestamp + nível + módulo + mensagem

## 🎨 Características do PDF

### **Layout Profissional**
- Fundo azul claro elegante (`#f0f4f8`)
- Fonte Helvetica moderna
- Cores sóbrias para contexto diplomático
- Bordas sutis no cabeçalho e título

### **Hierarquia Visual**
- **Título principal:** 18pt, cinza escuro
- **Data:** 12pt, formato "dd de mês de ano"
- **Cabeçalho:** 10pt, "Embaixada do Brasil em Nova Délhi"
- **Resumos:** 9pt, espaçamento simples
- **Descrição:** 9pt, itálico

### **Conteúdo**
- Resumos em inglês dos documentos originais
- Links clicáveis para documentos completos
- Organização por seções (Press Releases, Speeches, Media Briefings)
- Mensagens para seções sem conteúdo

## 🔧 Tecnologias Utilizadas

- **Python 3.8+**
- **BeautifulSoup4** - Scraping HTML
- **Google Gemini API** - Sumarização com IA
- **ReportLab** - Geração de PDFs
- **APScheduler** - Agendamento de tarefas
- **SMTP** - Envio de e-mails
- **Loguru** - Sistema de logs

## 📝 Exemplo de E-mail

```
Prezados/as colegas,

Segue o Boletim Diplomático de 07/08/2025.

Atenciosamente,
Taciano S. Zimmermann
```

## 🛠️ Desenvolvimento

### **Estrutura de Dados**
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

### **Testes**
```bash
python test_email.py  # Teste completo de geração e envio
```

## 📄 Licença

Este projeto é desenvolvido para uso interno da Embaixada do Brasil em Nova Délhi.

## 🤝 Contribuição

Para contribuições, entre em contato com a equipe de desenvolvimento.

## 📞 Contato

**Desenvolvido por:** Taciano S. Zimmermann  
**Instituição:** Embaixada do Brasil em Nova Délhi  
**Repositório:** https://github.com/tacianoz/boletim-diplomatico 