"""
Serviço de envio de e-mails via Gmail API.
Envia e-mails formatados em HTML usando a conta autenticada.
"""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

import config


class EmailService:
    """Envia e-mails através da API do Gmail."""

    def __init__(self, credentials: Credentials):
        """
        Inicializa o serviço do Gmail.

        Args:
            credentials: Credenciais autenticadas do Google.
        """
        self._service = build("gmail", "v1", credentials=credentials)

    def send_email(self, to_email: str, to_name: str, subject: str, html_body: str) -> dict:
        """
        Envia um e-mail formatado em HTML.

        Args:
            to_email: Endereço de e-mail do destinatário.
            to_name: Nome do destinatário.
            subject: Assunto do e-mail.
            html_body: Corpo do e-mail em HTML.

        Returns:
            Resposta da API do Gmail com o ID da mensagem enviada.

        Raises:
            Exception: Se houver erro no envio.
        """
        message = MIMEMultipart("alternative")
        message["To"] = f"{to_name} <{to_email}>"
        message["Subject"] = subject
        message["From"] = config.SENDER_NAME

        # Versão texto plano (fallback)
        # Remove tags HTML básicas para criar versão texto
        import re
        text_body = re.sub(r"<[^>]+>", "", html_body)
        text_body = re.sub(r"\s+", " ", text_body).strip()

        part_text = MIMEText(text_body, "plain", "utf-8")
        part_html = MIMEText(html_body, "html", "utf-8")

        message.attach(part_text)
        message.attach(part_html)

        # Codifica a mensagem em base64 URL-safe
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode("utf-8")

        # Envia via Gmail API
        result = self._service.users().messages().send(
            userId="me",
            body={"raw": raw_message},
        ).execute()

        return result
