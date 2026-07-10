# 🤖 Agente de Agradecimento a Doadores

Agente de IA que automatiza o envio de e-mails de agradecimento personalizados para doadores, usando **Google Sheets**, **Gmail** e **Google Gemini**.

## 📋 Como Funciona

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Google Sheets   │────▶│  Gemini IA   │────▶│   Gmail     │────▶│ Atualiza     │
│  (Lê pendentes)  │     │ (Gera e-mail)│     │ (Envia)     │     │  Planilha    │
└─────────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

1. **Lê** a planilha e identifica doadores com status `Pendente`
2. **Gera** um e-mail personalizado com IA (Google Gemini)
3. **Envia** o e-mail via Gmail
4. **Atualiza** a planilha → status `Enviado` + data/hora

---

## 🗂️ Estrutura da Planilha

A planilha **Doadores_Agradecimento_IA** deve ter a seguinte estrutura:

| Coluna | Campo              | Exemplo                  |
|--------|--------------------|--------------------------|
| A      | Nome do Doador     | Maria Silva              |
| B      | E-mail             | maria@email.com          |
| C      | Valor da Doação    | 150,00                   |
| D      | Data da Doação     | 10/07/2026               |
| E      | Tipo de Doação     | Pix                      |
| F      | Status             | Pendente                 |
| G      | Data de Envio      | *(preenchido pelo agente)* |

> ⚠️ A primeira linha deve ser o cabeçalho. Os dados começam na linha 2.

---

## 🚀 Configuração Passo a Passo

### 1. Pré-requisitos

- Python 3.10+ instalado
- Uma conta Google (Gmail)
- Acesso à planilha no Google Sheets

### 2. Criar ambiente virtual e instalar dependências

```bash
cd /home/italo/Documentos/Agente_Agradecimento_Doadores
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar APIs do Google (Sheets + Gmail)

#### 3.1 Criar um projeto no Google Cloud

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto (ou selecione um existente)
3. Ative as APIs necessárias:
   - **Google Sheets API** → [Ativar](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
   - **Gmail API** → [Ativar](https://console.cloud.google.com/apis/library/gmail.googleapis.com)

#### 3.2 Criar credenciais OAuth 2.0

1. No Google Cloud Console, vá em **APIs e Serviços → Credenciais**
2. Clique em **"Criar credenciais" → "ID do cliente OAuth"**
3. Se necessário, configure a **Tela de consentimento OAuth**:
   - Tipo: **Externo**
   - Preencha o nome do app e e-mail
   - Em **Escopos**, adicione:
     - `https://www.googleapis.com/auth/spreadsheets`
     - `https://www.googleapis.com/auth/gmail.send`
   - Em **Usuários de teste**, adicione seu e-mail Gmail
4. Ao criar o ID do cliente OAuth:
   - Tipo: **App para computador**
   - Baixe o arquivo JSON
5. **Renomeie** o arquivo para `credentials.json` e coloque na raiz do projeto

### 4. Obter chave da API Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/apikey)
2. Crie uma API Key
3. Copie a chave

### 5. Configurar o arquivo `.env`

Edite o arquivo `.env` na raiz do projeto:

```env
GOOGLE_SHEET_ID=1e64nxnkTT0vpaA3ftkHPABbaCWpQh4TaeakFPWHfcj8
SHEET_TAB_NAME=Página1
GEMINI_API_KEY=sua_chave_gemini_aqui
ORGANIZATION_NAME=Nome da Sua Organização
SENDER_NAME=Equipe de Agradecimento
```

> 💡 O `SHEET_TAB_NAME` deve corresponder ao nome da aba na sua planilha.
> Se a aba se chamar "Sheet1" ou "Folha1", ajuste de acordo.

---

## ▶️ Executar o Agente

```bash
source venv/bin/activate
python main.py
```

Na **primeira execução**, o navegador abrirá para autenticação Google.
Autorize o acesso ao Sheets e Gmail. O token será salvo em `token.json` para reutilização.

---

## 📁 Estrutura do Projeto

```
Agente_Agradecimento_Doadores/
├── main.py              # Script principal (orquestrador)
├── config.py            # Configurações e variáveis de ambiente
├── auth_service.py      # Autenticação OAuth2 do Google
├── sheets_service.py    # Integração com Google Sheets
├── ai_service.py        # Geração de e-mails com Gemini
├── email_service.py     # Envio de e-mails via Gmail
├── requirements.txt     # Dependências Python
├── .env                 # Variáveis de ambiente (NÃO commitar!)
├── .env.example         # Modelo do .env
├── .gitignore           # Arquivos ignorados pelo Git
├── credentials.json     # Credenciais OAuth2 (NÃO commitar!)
└── token.json           # Token de autenticação (gerado automaticamente)
```

---

## 🔒 Segurança

- **NUNCA** commite os arquivos `.env`, `credentials.json` ou `token.json`
- Eles já estão no `.gitignore`
- Use **Usuários de teste** na tela de consentimento OAuth enquanto o app não for verificado

---

## 🛠️ Solução de Problemas

| Problema | Solução |
|----------|---------|
| `credentials.json não encontrado` | Baixe o arquivo OAuth do Google Cloud Console |
| `GOOGLE_SHEET_ID não configurado` | Verifique o arquivo `.env` |
| `Erro 403 no Sheets` | Verifique se a API do Sheets está ativada e se você tem acesso à planilha |
| `Erro 403 no Gmail` | Verifique se a API do Gmail está ativada e se o escopo `gmail.send` foi autorizado |
| `Token expirado` | Delete o `token.json` e execute novamente para re-autenticar |
| `Nenhum doador pendente` | Verifique se a coluna F tem o valor exato `Pendente` |
