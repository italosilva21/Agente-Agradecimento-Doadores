"""
Configurações centralizadas do Agente de Agradecimento.
Carrega variáveis de ambiente e define constantes do projeto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Caminho base do projeto (diretório onde este arquivo está)
BASE_DIR = Path(__file__).parent

# Carrega variáveis do arquivo .env (caminho explícito para garantir que funcione)
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# ──────────────────────────────────────────────
# Google Sheets
# ──────────────────────────────────────────────
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
SHEET_TAB_NAME = os.getenv("SHEET_TAB_NAME", "Página1")

# Escopos necessários para Google Sheets + Gmail
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
]

# Caminho do arquivo de credenciais OAuth2
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# ──────────────────────────────────────────────
# Google Gemini (IA)
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.5-flash"

# ──────────────────────────────────────────────
# E-mail
# ──────────────────────────────────────────────
ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME", "Nossa Organização")
SENDER_NAME = os.getenv("SENDER_NAME", "Equipe de Agradecimento")

# ──────────────────────────────────────────────
# Colunas esperadas na planilha
# ──────────────────────────────────────────────
# A planilha deve ter as seguintes colunas (nesta ordem):
#   A: Nome do Doador
#   B: E-mail
#   C: Valor da Doação
#   D: Data da Doação
#   E: Tipo de Doação (ex: Pix, Cartão, Boleto)
#   F: Status ("Pendente" ou "Enviado")
#   G: Data de Envio do E-mail
COLUMN_MAP = {
    "nome": 0,
    "email": 1,
    "valor": 2,
    "data_doacao": 3,
    "tipo_doacao": 4,
    "status": 5,
    "data_envio": 6,
}

STATUS_PENDENTE = "Pendente"
STATUS_ENVIADO = "Enviado"


def validate_config():
    """Valida se todas as configurações obrigatórias estão preenchidas."""
    errors = []

    if not GOOGLE_SHEET_ID:
        errors.append("GOOGLE_SHEET_ID não configurado no .env")
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY não configurado no .env")
    if not CREDENTIALS_FILE.exists():
        errors.append(
            f"Arquivo credentials.json não encontrado em {CREDENTIALS_FILE}.\n"
            "   Baixe-o do Google Cloud Console (OAuth 2.0 Client ID)."
        )

    if errors:
        print("\n❌ Erros de configuração encontrados:\n")
        for err in errors:
            print(f"   • {err}")
        print("\nConsulte o README.md para instruções de configuração.\n")
        sys.exit(1)
