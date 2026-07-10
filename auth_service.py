"""
Serviço de autenticação Google OAuth2.
Gerencia o fluxo de autenticação e armazena o token localmente.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import config


def get_google_credentials() -> Credentials:
    """
    Obtém credenciais válidas do Google.

    Na primeira execução, abre o navegador para autenticação.
    Nas execuções seguintes, reutiliza o token salvo em token.json.

    Returns:
        Credentials: Credenciais autenticadas do Google.
    """
    creds = None

    # Tenta carregar token existente
    if config.TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(config.TOKEN_FILE), config.GOOGLE_SCOPES
        )

    # Se não há credenciais válidas, realiza autenticação
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(config.CREDENTIALS_FILE), config.GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Salva o token para reutilização
        with open(config.TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds
