
# Agente de Agradecimento a Doadores com IA

Este projeto cria um agente inteligente que automatiza o envio de e-mails de agradecimento para doadores.

O sistema lê os dados dos doadores em uma planilha Google Sheets, identifica quem ainda precisa receber o agradecimento, utiliza o Gemini IA para criar uma mensagem personalizada e envia o e-mail automaticamente pelo Gmail.

## VEG aplicado

**Visão:** Criar uma automação para facilitar o contato com doadores e reduzir o trabalho manual.

**Link:** Integração com Google Sheets, Gmail API e Gemini API.

**Arquitetura:** O fluxo funciona assim:

Google Sheets → Agente Python → Gemini IA → Gmail → Atualização da planilha.

**Estilo:** Os e-mails são personalizados, profissionais e escritos de forma humanizada.

**Gatilho:** O agente é executado pelo comando `python main.py` e processa os doadores pendentes automaticamente.

## Arquivos do projeto

* main.py: controla o fluxo principal.
* ai_service.py: conexão com Gemini IA.
* sheets_service.py: leitura e atualização da planilha.
* email_service.py: envio dos e-mails.
* auth_service.py: autenticação Google.

## Commits

* feat: cria agente de agradecimento com Gemini Gmail e Sheets
* docs: adiciona resultado final do projeto

O projeto demonstra uma automação completa utilizando inteligência artificial, APIs e integração com serviços Google.
