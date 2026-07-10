"""
Serviço de integração com o Google Sheets.
Lê doadores pendentes e atualiza o status após envio.
"""

from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

import config


class SheetsService:
    """Gerencia operações de leitura/escrita na planilha de doadores."""

    def __init__(self, credentials: Credentials):
        """
        Inicializa o serviço do Google Sheets.

        Args:
            credentials: Credenciais autenticadas do Google.
        """
        service = build("sheets", "v4", credentials=credentials)
        self._sheet = service.spreadsheets()

    def get_pending_donors(self) -> list[dict]:
        """
        Lê a planilha e retorna apenas doadores com status 'Pendente'.

        Returns:
            Lista de dicionários com os dados de cada doador pendente,
            incluindo o número da linha na planilha (para atualização posterior).
        """
        range_name = f"{config.SHEET_TAB_NAME}!A2:G"
        result = self._sheet.values().get(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=range_name,
        ).execute()

        rows = result.get("values", [])
        pending_donors = []

        for i, row in enumerate(rows):
            # Garante que a linha tenha colunas suficientes
            while len(row) < 7:
                row.append("")

            status = row[config.COLUMN_MAP["status"]].strip()

            if status.lower() == config.STATUS_PENDENTE.lower():
                pending_donors.append({
                    "row_number": i + 2,  # +2 porque começa na linha 2 (1-indexed + header)
                    "nome": row[config.COLUMN_MAP["nome"]].strip(),
                    "email": row[config.COLUMN_MAP["email"]].strip(),
                    "valor": row[config.COLUMN_MAP["valor"]].strip(),
                    "data_doacao": row[config.COLUMN_MAP["data_doacao"]].strip(),
                    "tipo_doacao": row[config.COLUMN_MAP["tipo_doacao"]].strip(),
                    "status": status,
                })

        return pending_donors

    def mark_as_sent(self, row_number: int) -> None:
        """
        Atualiza o status de um doador para 'Enviado' e registra a data/hora.

        Args:
            row_number: Número da linha na planilha (1-indexed).
        """
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Atualiza colunas F (status) e G (data de envio)
        range_name = f"{config.SHEET_TAB_NAME}!F{row_number}:G{row_number}"
        body = {
            "values": [[config.STATUS_ENVIADO, now]]
        }

        self._sheet.values().update(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def get_sheet_info(self) -> Optional[dict]:
        """
        Retorna informações básicas da planilha para validação.

        Returns:
            Dicionário com título e informações das abas, ou None em caso de erro.
        """
        try:
            result = self._sheet.get(
                spreadsheetId=config.GOOGLE_SHEET_ID,
            ).execute()
            return {
                "title": result.get("properties", {}).get("title", ""),
                "sheets": [
                    s.get("properties", {}).get("title", "")
                    for s in result.get("sheets", [])
                ],
            }
        except Exception:
            return None
