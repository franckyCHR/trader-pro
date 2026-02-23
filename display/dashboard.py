"""
Interface visuelle du terminal - affiche l'analyse comme un vrai trader.
Utilise Rich pour un rendu professionnel directement dans le terminal.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.align import Align

from brain.trader_mind import DecisionTrader, Signal, ForceDuSignal

console = Console()

# Couleurs par signal
COULEURS_SIGNAL = {
    Signal.ACHAT:    "bold green",
    Signal.VENTE:    "bold red",
    Signal.ATTENDRE: "bold yellow",
}

EMOJIS_SIGNAL = {
    Signal.ACHAT:    "▲ ACHAT",
    Signal.VENTE:    "▼ VENTE",
    Signal.ATTENDRE: "◆ ATTENDRE",
}

COULEURS_FORCE = {
    ForceDuSignal.FORT:   "green",
    ForceDuSignal.MOYEN:  "yellow",
    ForceDuSignal.FAIBLE: "red",
}


def afficher_banniere():
    """Affiche le logo de l'application."""
    banniere = """
████████╗██████╗  █████╗ ██████╗ ███████╗██████╗     ██████╗ ██████╗  ██████╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔═══██╗
   ██║   ██████╔╝███████║██║  ██║█████╗  ██████╔╝    ██████╔╝██████╔╝██║   ██║
   ██║   ██╔══██╗██╔══██║██║  ██║██╔══╝  ██╔══██╗    ██╔═══╝ ██╔══██╗██║   ██║
   ██║   ██║  ██║██║  ██║██████╔╝███████╗██║  ██║    ██║     ██║  ██║╚██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝
"""
    console.print(Align.center(banniere), style="bold cyan")
    console.print(Align.center(
        "Basé sur les principes des traders particuliers gagnants\n"
        '"Le trader gagnant applique son plan sans fantaisie." - Traders Pro'
    ), style="italic dim")
    console.print()


def afficher_chargement(message: str):
    """Affiche un spinner pendant le chargement des données."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def barre_score(score: int, largeur: int = 20) -> str:
    """Génère une barre de progression ASCII pour le score de confiance."""
    rempli = int((score / 100) * largeur)
    vide = largeur - rempli

    if score >= 75:
        couleur = "green"
    elif score >= 50:
        couleur = "yellow"
    else:
        couleur = "red"

    barre = f"[{couleur}]{'█' * rempli}[/{couleur}]{'░' * vide}"
    return barre


def afficher_decision(decision: DecisionTrader):
    """Affiche la décision complète du cerveau du trader."""

    console.print()
    console.print(Rule(f"[bold]ANALYSE : {decision.paire} [{decision.timeframe}][/bold]"))
    console.print()

    couleur = COULEURS_SIGNAL[decision.signal]
    emoji_signal = EMOJIS_SIGNAL[decision.signal]

    # --- SIGNAL PRINCIPAL ---
    force_style = COULEURS_FORCE[decision.force]
    signal_markup = (
        f"  [{couleur}]{emoji_signal}[/{couleur}]  "
        f"Score : [bold]{decision.score_confiance}/100[/bold]  "
        f"{barre_score(decision.score_confiance)}  "
        f"Force : [{force_style}]{decision.force.value}[/{force_style}]"
    )

    console.print(Panel(
        signal_markup,
        title="[bold]SIGNAL DU TRADER[/bold]",
        border_style=couleur.replace("bold ", ""),
        padding=(0, 2),
    ))

    # --- PRIX ACTUEL ---
    console.print(f"  Prix actuel : [bold cyan]{decision.prix_actuel:.5f}[/bold cyan]  "
                  f"(Dernière mise à jour : {decision.tendance.ma20:.5f} MA20)")

    console.print()

    # --- ANALYSE EN 2 COLONNES ---
    table_tendance = Table(
        title="Tendance", box=box.ROUNDED, show_header=True,
        header_style="bold blue", min_width=35
    )
    table_tendance.add_column("Indicateur", style="cyan", no_wrap=True)
    table_tendance.add_column("Valeur", style="white", justify="right")
    table_tendance.add_column("Etat", justify="center")

    # Direction
    dir_color = "green" if decision.tendance.direction == "HAUSSE" else \
                "red" if decision.tendance.direction == "BAISSE" else "yellow"
    table_tendance.add_row(
        "Direction",
        decision.tendance.direction,
        f"[{dir_color}]{'▲' if decision.tendance.direction == 'HAUSSE' else '▼' if decision.tendance.direction == 'BAISSE' else '—'}[/{dir_color}]"
    )
    table_tendance.add_row(
        "MA20",
        f"{decision.tendance.ma20:.5f}",
        "[green]↑[/green]" if decision.tendance.pente_ma20 > 0 else "[red]↓[/red]"
    )
    table_tendance.add_row("MA50", f"{decision.tendance.ma50:.5f}", "")
    table_tendance.add_row("MA200", f"{decision.tendance.ma200:.5f}", "")
    table_tendance.add_row(
        "Pente MA20",
        f"{decision.tendance.pente_ma20:+.3f}%",
        "[green]Haussière[/green]" if decision.tendance.pente_ma20 > 0 else "[red]Baissière[/red]"
    )

    table_momentum = Table(
        title="Momentum", box=box.ROUNDED, show_header=True,
        header_style="bold magenta", min_width=35
    )
    table_momentum.add_column("Indicateur", style="cyan", no_wrap=True)
    table_momentum.add_column("Valeur", style="white", justify="right")
    table_momentum.add_column("Zone", justify="center")

    rsi_color = "red" if decision.momentum.rsi >= 70 else \
                "green" if decision.momentum.rsi <= 30 else "white"
    table_momentum.add_row(
        "RSI (14)",
        f"[{rsi_color}]{decision.momentum.rsi:.1f}[/{rsi_color}]",
        f"[{rsi_color}]{decision.momentum.rsi_zone}[/{rsi_color}]"
    )

    macd_color = "green" if decision.momentum.macd_signal == "HAUSSIER" else \
                 "red" if decision.momentum.macd_signal == "BAISSIER" else "yellow"
    table_momentum.add_row(
        "MACD",
        f"{decision.momentum.macd_valeur:.6f}",
        f"[{macd_color}]{decision.momentum.macd_signal}[/{macd_color}]"
    )
    table_momentum.add_row("Signal MACD", f"{decision.momentum.macd_signal_valeur:.6f}", "")
    table_momentum.add_row(
        "Histogramme",
        f"{decision.momentum.macd_histogramme:+.6f}",
        "[green]▲[/green]" if decision.momentum.macd_histogramme > 0 else "[red]▼[/red]"
    )

    console.print(Columns([table_tendance, table_momentum]))

    # --- GESTION DU RISQUE ---
    if decision.gestion_risque:
        gr = decision.gestion_risque
        console.print()

        table_risque = Table(
            title="Gestion du Risque - Plan de Trade",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold white on dark_green" if decision.signal == Signal.ACHAT
                         else "bold white on dark_red",
            min_width=70
        )
        table_risque.add_column("Niveau", style="bold cyan", min_width=20)
        table_risque.add_column("Prix", style="bold white", justify="right", min_width=15)
        table_risque.add_column("Distance", style="dim", justify="right", min_width=12)
        table_risque.add_column("Pips", style="dim", justify="right", min_width=10)

        table_risque.add_row(
            "ENTRÉE",
            f"[bold]{gr.prix_entree:.5f}[/bold]",
            "—", "—"
        )
        table_risque.add_row(
            "[red]STOP LOSS[/red]",
            f"[red bold]{gr.stop_loss:.5f}[/red bold]",
            f"[red]{abs(gr.prix_entree - gr.stop_loss):.5f}[/red]",
            f"[red]{gr.risque_en_pips:.0f}[/red]"
        )
        table_risque.add_row(
            "[green]TAKE PROFIT 1[/green]",
            f"[green bold]{gr.take_profit_1:.5f}[/green bold]",
            f"[green]{abs(gr.prix_entree - gr.take_profit_1):.5f}[/green]",
            f"[green]{gr.gain_potentiel_pips:.0f}[/green]"
        )
        table_risque.add_row(
            "[bright_green]TAKE PROFIT 2[/bright_green]",
            f"[bright_green bold]{gr.take_profit_2:.5f}[/bright_green bold]",
            f"[bright_green]{abs(gr.prix_entree - gr.take_profit_2):.5f}[/bright_green]",
            f"[bright_green]{gr.gain_potentiel_pips * (4.0/2.5):.0f}[/bright_green]"
        )

        console.print(table_risque)

        rr_color = "green" if gr.ratio_risque_rendement >= 2 else "yellow"
        console.print(
            f"  Ratio R/R : [{rr_color}]1:{gr.ratio_risque_rendement:.1f}[/{rr_color}]  |  "
            f"Taille position : [bold]{gr.taille_position} lots[/bold]  |  "
            f"Capital risqué : [yellow]{gr.capital_risque_pct}%[/yellow]  |  "
            f"ATR : {gr.atr:.5f}"
        )

    # --- RAISONS DU SIGNAL ---
    console.print()
    if decision.raisons:
        table_raisons = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table_raisons.add_column("", style="green", no_wrap=True, width=3)
        table_raisons.add_column("Raison", style="white")
        for raison in decision.raisons:
            table_raisons.add_row("✓", raison)
        console.print(Panel(table_raisons, title="[bold green]Pourquoi ce signal ?[/bold green]",
                            border_style="green", padding=(0, 1)))

    # --- AVERTISSEMENTS ---
    if decision.avertissements:
        table_avert = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table_avert.add_column("", style="yellow", no_wrap=True, width=3)
        table_avert.add_column("Avertissement", style="yellow")
        for avert in decision.avertissements:
            table_avert.add_row("⚠", avert)
        console.print(Panel(table_avert, title="[bold yellow]Points d'attention[/bold yellow]",
                            border_style="yellow", padding=(0, 1)))

    # --- CONSEIL DU TRADER ---
    console.print()
    console.print(Panel(
        Align.center(f'[italic]"{decision.conseil_du_trader}"[/italic]'),
        title="[bold cyan]Le Trader Pro dit :[/bold cyan]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()


def afficher_menu_marches(marches: dict) -> None:
    """Affiche le menu des marchés disponibles."""
    console.print()
    console.print(Rule("[bold]MARCHÉS DISPONIBLES[/bold]"))
    console.print()

    for idx_cat, (categorie, symboles) in enumerate(marches.items()):
        style_titre = "bold green" if "Forex" in categorie else \
                      "bold blue" if "Indices" in categorie else "bold yellow"
        console.print(f"  [{style_titre}]{categorie}[/{style_titre}]")

        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("N°", style="dim", width=5)
        table.add_column("Paire", style="cyan bold")

        for idx, nom in enumerate(symboles, start=1):
            table.add_row(str(idx), nom)

        console.print(table)
        console.print()


def afficher_erreur(message: str):
    """Affiche un message d'erreur."""
    console.print(Panel(
        f"[red]{message}[/red]",
        title="[bold red]ERREUR[/bold red]",
        border_style="red"
    ))


def afficher_info(message: str):
    """Affiche un message informatif."""
    console.print(f"[dim cyan]ℹ  {message}[/dim cyan]")
