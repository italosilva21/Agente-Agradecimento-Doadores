"""
🤖 Agente de Agradecimento a Doadores
======================================
Script principal que orquestra todo o fluxo:
1. Lê doadores pendentes do Google Sheets
2. Gera e-mails personalizados com IA (Gemini)
3. Envia os e-mails via Gmail
4. Atualiza a planilha com o status "Enviado"
"""

import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

import config
from auth_service import get_google_credentials
from sheets_service import SheetsService
from ai_service import AIService
from email_service import EmailService

console = Console()


def display_banner():
    """Exibe o banner inicial do agente."""
    banner = """
[bold magenta]🤖 Agente de Agradecimento a Doadores[/bold magenta]
[dim]Automatização inteligente de e-mails de agradecimento[/dim]
[dim]Powered by Google Gemini + Gmail + Sheets[/dim]
    """
    console.print(Panel(banner.strip(), border_style="magenta", padding=(1, 2)))
    console.print()


def display_donors_table(donors: list[dict]):
    """Exibe uma tabela formatada com os doadores pendentes."""
    table = Table(
        title="📋 Doadores Pendentes",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Nome", style="bold white")
    table.add_column("E-mail", style="blue")
    table.add_column("Valor (R$)", justify="right", style="green")
    table.add_column("Data", style="yellow")
    table.add_column("Tipo", style="magenta")

    for i, donor in enumerate(donors, 1):
        table.add_row(
            str(i),
            donor["nome"],
            donor["email"],
            donor["valor"],
            donor["data_doacao"],
            donor["tipo_doacao"],
        )

    console.print(table)
    console.print()


def process_donor(
    donor: dict,
    ai_service: AIService,
    email_service: EmailService,
    sheets_service: SheetsService,
    index: int,
    total: int,
) -> bool:
    """
    Processa um único doador: gera e-mail com IA, envia e atualiza planilha.

    Returns:
        True se o processamento foi bem-sucedido, False caso contrário.
    """
    donor_name = donor["nome"]
    donor_email = donor["email"]

    console.print(
        f"\n[bold]──── Doador {index}/{total}: {donor_name} ────[/bold]"
    )

    try:
        # Passo 1: Gerar e-mail com IA
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🧠 Gerando e-mail com IA...", total=None)
            email_data = ai_service.generate_thank_you_email(donor)
            progress.update(task, description="✅ E-mail gerado!")

        console.print(f"   📧 Assunto: [italic]{email_data['subject']}[/italic]")

        # Passo 2: Enviar e-mail
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"📤 Enviando para {donor_email}...", total=None
            )
            result = email_service.send_email(
                to_email=donor_email,
                to_name=donor_name,
                subject=email_data["subject"],
                html_body=email_data["body"],
            )
            progress.update(task, description="✅ E-mail enviado!")

        msg_id = result.get("id", "N/A")
        console.print(f"   🆔 ID da mensagem: [dim]{msg_id}[/dim]")

        # Passo 3: Atualizar planilha
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("📝 Atualizando planilha...", total=None)
            sheets_service.mark_as_sent(donor["row_number"])
            progress.update(task, description="✅ Planilha atualizada!")

        console.print(f"   ✅ [bold green]{donor_name} processado com sucesso![/bold green]")

        # Pequena pausa para não sobrecarregar as APIs
        time.sleep(2)

        return True

    except Exception as e:
        console.print(f"   ❌ [bold red]Erro ao processar {donor_name}:[/bold red] {e}")
        return False


def main():
    """Função principal que orquestra o fluxo do agente."""
    display_banner()

    # ── Validação de configuração ──
    console.print("[bold]🔧 Verificando configuração...[/bold]")
    config.validate_config()
    console.print("   ✅ Configuração válida\n")

    # ── Autenticação Google ──
    console.print("[bold]🔐 Autenticando com Google...[/bold]")
    credentials = get_google_credentials()
    console.print("   ✅ Autenticado com sucesso\n")

    # ── Inicialização dos serviços ──
    sheets_service = SheetsService(credentials)
    ai_service = AIService()
    email_service = EmailService(credentials)

    # ── Verificar conexão com a planilha ──
    console.print("[bold]📊 Conectando à planilha...[/bold]")
    sheet_info = sheets_service.get_sheet_info()
    if sheet_info:
        console.print(f"   📄 Planilha: [cyan]{sheet_info['title']}[/cyan]")
        console.print(f"   📑 Abas: {', '.join(sheet_info['sheets'])}\n")
    else:
        console.print("   ⚠️  Não foi possível obter informações da planilha\n")

    # ── Buscar doadores pendentes ──
    console.print("[bold]🔍 Buscando doadores pendentes...[/bold]")
    pending_donors = sheets_service.get_pending_donors()

    if not pending_donors:
        console.print(
            Panel(
                "✨ Nenhum doador pendente encontrado!\n"
                "Todos os agradecimentos já foram enviados.",
                title="Tudo em dia!",
                border_style="green",
            )
        )
        return

    console.print(f"   📬 Encontrados [bold]{len(pending_donors)}[/bold] doadores pendentes\n")
    display_donors_table(pending_donors)

    # ── Confirmação do usuário ──
    console.print(
        f"[bold yellow]⚡ Deseja enviar {len(pending_donors)} e-mail(s) de agradecimento?[/bold yellow]"
    )
    response = input("   Digite 's' para confirmar ou 'n' para cancelar: ").strip().lower()

    if response != "s":
        console.print("\n[dim]Operação cancelada pelo usuário.[/dim]")
        return

    # ── Processamento dos doadores ──
    console.print(
        f"\n[bold magenta]🚀 Iniciando processamento de {len(pending_donors)} doadores...[/bold magenta]\n"
    )

    success_count = 0
    error_count = 0

    for i, donor in enumerate(pending_donors, 1):
        success = process_donor(
            donor=donor,
            ai_service=ai_service,
            email_service=email_service,
            sheets_service=sheets_service,
            index=i,
            total=len(pending_donors),
        )
        if success:
            success_count += 1
        else:
            error_count += 1

    # ── Relatório final ──
    console.print("\n")
    summary = f"""
[bold]📊 Relatório Final[/bold]

   ✅ Enviados com sucesso: [bold green]{success_count}[/bold green]
   ❌ Erros: [bold red]{error_count}[/bold red]
   📧 Total processado: [bold]{success_count + error_count}[/bold]
    """
    console.print(
        Panel(
            summary.strip(),
            title="Processamento Concluído",
            border_style="magenta",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[dim]Operação interrompida pelo usuário.[/dim]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Erro fatal:[/bold red] {e}")
        sys.exit(1)
