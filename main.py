"""
TRADER PRO - Application d'analyse de trading
===============================================
Basée sur les principes du livre "Les secrets des traders particuliers qui gagnent"

Utilisation:
    python main.py                  # Mode interactif (menu)
    python main.py --paire EUR/USD  # Analyser une paire directement
    python main.py --scan           # Scanner toutes les paires Forex
    python main.py --liste          # Lister les marchés disponibles

Architecture:
    brain/trader_mind.py    → Le cerveau: logique de décision
    data/market_data.py     → Récupération des données marché
    analysis/technicals.py  → Calcul des indicateurs techniques
    display/dashboard.py    → Affichage terminal (interface)
"""

import sys
import argparse
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

from brain.trader_mind import TraderBrain
from data.market_data import (
    get_donnees_paire, lister_marches,
    PAIRES_FOREX, TOUS_LES_MARCHES
)
from analysis.technicals import ajouter_tous_les_indicateurs, extraire_valeurs_actuelles
from display.dashboard import (
    console, afficher_banniere, afficher_decision,
    afficher_menu_marches, afficher_erreur, afficher_info
)


def analyser_paire(paire: str, timeframe: str = "1j",
                   capital: float = 1000.0) -> bool:
    """
    Lance l'analyse complète d'une paire.
    Retourne True si succès, False si erreur.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Chargement des données {paire}...", total=None)

        try:
            # 1. Téléchargement des données
            df = get_donnees_paire(paire, timeframe)
            progress.update(task, description=f"Calcul des indicateurs {paire}...")

            # 2. Calcul des indicateurs techniques
            df = ajouter_tous_les_indicateurs(df)

            if len(df) < 50:
                afficher_erreur(
                    f"Pas assez de données pour {paire} "
                    f"({len(df)} bougies, minimum 50 requises)"
                )
                return False

            # 3. Extraction des valeurs actuelles
            valeurs = extraire_valeurs_actuelles(df)
            progress.update(task, description="Analyse du cerveau du trader...")

            # 4. Décision du cerveau du trader
            cerveau = TraderBrain()
            decision = cerveau.analyser(
                paire=paire,
                timeframe=timeframe,
                prix=valeurs["prix"],
                ma20=valeurs["ma20"],
                ma50=valeurs["ma50"],
                ma200=valeurs["ma200"],
                historique_ma20=valeurs["historique_ma20"],
                rsi=valeurs["rsi"],
                macd=valeurs["macd"],
                macd_signal_val=valeurs["macd_signal"],
                macd_hist=valeurs["macd_hist"],
                atr=valeurs["atr"],
                capital=capital,
                decimales=5 if "/" in paire else 2,
            )

        except Exception as e:
            afficher_erreur(f"Erreur lors de l'analyse de {paire}: {str(e)}")
            return False

    # 5. Affichage de la décision
    afficher_decision(decision)
    return True


def mode_scan(timeframe: str = "1j", capital: float = 1000.0):
    """
    Scanne toutes les paires Forex et affiche un résumé des signaux.
    Utile pour identifier rapidement les meilleures opportunités.
    """
    from rich.table import Table
    from rich import box
    from brain.trader_mind import Signal

    console.print()
    console.print("[bold cyan]SCAN FOREX - Toutes les paires[/bold cyan]")
    console.print("[dim]Analyse en cours, patientez...[/dim]")
    console.print()

    resultats = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scan...", total=len(PAIRES_FOREX))

        for paire in PAIRES_FOREX.keys():
            progress.update(task, description=f"Analyse {paire}...")
            try:
                df = get_donnees_paire(paire, timeframe)
                df = ajouter_tous_les_indicateurs(df)

                if len(df) < 50:
                    progress.advance(task)
                    continue

                valeurs = extraire_valeurs_actuelles(df)
                cerveau = TraderBrain()
                decision = cerveau.analyser(
                    paire=paire,
                    timeframe=timeframe,
                    prix=valeurs["prix"],
                    ma20=valeurs["ma20"],
                    ma50=valeurs["ma50"],
                    ma200=valeurs["ma200"],
                    historique_ma20=valeurs["historique_ma20"],
                    rsi=valeurs["rsi"],
                    macd=valeurs["macd"],
                    macd_signal_val=valeurs["macd_signal"],
                    macd_hist=valeurs["macd_hist"],
                    atr=valeurs["atr"],
                    capital=capital,
                )
                resultats.append(decision)

            except Exception:
                pass
            finally:
                progress.advance(task)

    # Tri: d'abord les signaux forts, puis par score
    resultats.sort(key=lambda d: (
        0 if d.signal != Signal.ATTENDRE else 1,
        -d.score_confiance
    ))

    # Tableau de résultats
    table = Table(
        title=f"Résultats du Scan Forex ({timeframe})",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white",
    )
    table.add_column("Paire", style="cyan bold", min_width=12)
    table.add_column("Prix", style="white", justify="right", min_width=12)
    table.add_column("Signal", justify="center", min_width=12)
    table.add_column("Score", justify="center", min_width=8)
    table.add_column("Tendance", justify="center", min_width=10)
    table.add_column("RSI", justify="right", min_width=8)
    table.add_column("SL", style="red", justify="right", min_width=12)
    table.add_column("TP1", style="green", justify="right", min_width=12)

    for d in resultats:
        signal_colors = {
            Signal.ACHAT: "[bold green]▲ ACHAT[/bold green]",
            Signal.VENTE: "[bold red]▼ VENTE[/bold red]",
            Signal.ATTENDRE: "[yellow]◆ ATTENDRE[/yellow]",
        }
        dir_colors = {
            "HAUSSE": "[green]▲ HAUSSE[/green]",
            "BAISSE": "[red]▼ BAISSE[/red]",
            "NEUTRE": "[yellow]— NEUTRE[/yellow]",
        }

        sl = f"{d.gestion_risque.stop_loss:.5f}" if d.gestion_risque else "—"
        tp = f"{d.gestion_risque.take_profit_1:.5f}" if d.gestion_risque else "—"

        score_color = "green" if d.score_confiance >= 70 else \
                      "yellow" if d.score_confiance >= 50 else "red"

        table.add_row(
            d.paire,
            f"{d.prix_actuel:.5f}",
            signal_colors[d.signal],
            f"[{score_color}]{d.score_confiance}[/{score_color}]",
            dir_colors.get(d.tendance.direction, d.tendance.direction),
            f"{d.momentum.rsi:.1f}",
            sl,
            tp,
        )

    console.print(table)
    console.print()

    # Résumé
    nb_achat = sum(1 for d in resultats if d.signal == Signal.ACHAT)
    nb_vente = sum(1 for d in resultats if d.signal == Signal.VENTE)
    nb_attendre = sum(1 for d in resultats if d.signal == Signal.ATTENDRE)
    console.print(
        f"  Résumé : [green]{nb_achat} ACHAT[/green] | "
        f"[red]{nb_vente} VENTE[/red] | "
        f"[yellow]{nb_attendre} ATTENDRE[/yellow]"
    )
    console.print()


def mode_interactif():
    """Mode interactif avec menu de sélection."""
    afficher_banniere()

    marches = lister_marches()
    tous_noms = list(TOUS_LES_MARCHES.keys())

    capital = 1000.0

    while True:
        console.print("[bold]Que voulez-vous faire ?[/bold]")
        console.print("  [cyan]1[/cyan] - Analyser une paire")
        console.print("  [cyan]2[/cyan] - Scanner tout le Forex")
        console.print("  [cyan]3[/cyan] - Voir les marchés disponibles")
        console.print("  [cyan]4[/cyan] - Changer le capital (actuel : "
                      f"[yellow]{capital:.0f}€[/yellow])")
        console.print("  [cyan]q[/cyan] - Quitter")
        console.print()

        choix = Prompt.ask(
            "[bold cyan]Votre choix[/bold cyan]",
            choices=["1", "2", "3", "4", "q"],
            default="1"
        )

        if choix == "q":
            console.print("\n[cyan]À bientôt ! Trade avec discipline.[/cyan]\n")
            break

        elif choix == "1":
            afficher_menu_marches(marches)
            paire = Prompt.ask(
                "[bold cyan]Entrez la paire à analyser[/bold cyan] (ex: EUR/USD)",
                default="EUR/USD"
            ).upper()

            if paire not in TOUS_LES_MARCHES:
                afficher_erreur(f"Paire '{paire}' introuvable.")
                continue

            timeframe = Prompt.ask(
                "[bold cyan]Timeframe[/bold cyan]",
                choices=["1h", "4h", "1j", "1sem"],
                default="1j"
            )

            analyser_paire(paire, timeframe, capital)

            if Confirm.ask("Analyser une autre paire ?", default=True):
                continue

        elif choix == "2":
            timeframe = Prompt.ask(
                "[bold cyan]Timeframe pour le scan[/bold cyan]",
                choices=["1h", "4h", "1j", "1sem"],
                default="1j"
            )
            mode_scan(timeframe, capital)

            if Confirm.ask("Analyser une paire en détail ?", default=False):
                paire = Prompt.ask("[bold cyan]Quelle paire ?[/bold cyan]").upper()
                if paire in TOUS_LES_MARCHES:
                    analyser_paire(paire, timeframe, capital)

        elif choix == "3":
            afficher_menu_marches(marches)

        elif choix == "4":
            capital = float(Prompt.ask(
                "[bold cyan]Montant de votre capital (€)[/bold cyan]",
                default=str(capital)
            ))
            afficher_info(f"Capital mis à jour : {capital:.0f}€")

        console.print()


def main():
    """Point d'entrée principal avec gestion des arguments CLI."""
    parser = argparse.ArgumentParser(
        description="Trader Pro - Analyse technique basée sur Traders_Pro.pdf"
    )
    parser.add_argument("--paire", type=str, help="Analyser une paire directement (ex: EUR/USD)")
    parser.add_argument("--timeframe", type=str, default="1j",
                        choices=["1h", "4h", "1j", "1sem"],
                        help="Timeframe d'analyse (défaut: 1j)")
    parser.add_argument("--capital", type=float, default=1000.0,
                        help="Capital en euros (défaut: 1000)")
    parser.add_argument("--scan", action="store_true",
                        help="Scanner toutes les paires Forex")
    parser.add_argument("--liste", action="store_true",
                        help="Lister tous les marchés disponibles")

    args = parser.parse_args()

    if args.liste:
        afficher_banniere()
        afficher_menu_marches(lister_marches())
        return

    if args.scan:
        afficher_banniere()
        mode_scan(args.timeframe, args.capital)
        return

    if args.paire:
        afficher_banniere()
        paire = args.paire.upper()
        if paire not in TOUS_LES_MARCHES:
            afficher_erreur(f"Paire '{paire}' inconnue. Utilisez --liste pour voir les marchés.")
            sys.exit(1)
        analyser_paire(paire, args.timeframe, args.capital)
        return

    # Mode interactif par défaut
    mode_interactif()


if __name__ == "__main__":
    main()
