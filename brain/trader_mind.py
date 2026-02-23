"""
LE CERVEAU DU TRADER - TraderBrain
====================================
Basé sur les principes du livre "Les secrets des traders particuliers qui gagnent"

PRINCIPES FONDAMENTAUX INTÉGRÉS (Traders_Pro.pdf) :
----------------------------------------------------
1. SUIVI DE TENDANCE : Acheter bas/vendre haut - identifier en un coup d'oeil la direction
2. PLAN DE TRADING : Appliquer le plan sans fantaisie, ne pas improviser
3. GESTION DU RISQUE : Ne JAMAIS perdre plus que prévu - sécuriser les positions
4. MATHÉMATIQUES : Les lois mathématiques simples permettent de gagner même en perdant 2x/3
5. ZÉRO ÉMOTION : Analyser le graphique avec une méthode précise, pas avec ses tripes
6. STOP-LOSS OBLIGATOIRE : Dimensionner les positions pour dormir tranquille la nuit
7. RAPPORT RISQUE/RENDEMENT : Toujours viser au minimum 1:2 (risquer 1 pour gagner 2)
8. COMPTE DÉMO D'ABORD : S'entraîner avant d'engager de l'argent réel

DIFFÉRENCES TRADER GAGNANT vs PERDANT (Chap. 5 du PDF) :
----------------------------------------------------------
PERDANT                              GAGNANT
- Aucun plan de trading              - Applique son plan religieusement
- Impulsif, décide comme au casino   - Analyse graphique méthodique
- Ignore les stats pour gagner       - Utilise les processus mathématiques
- Laisse ses émotions exploser       - Méthode de repérage graphique précise
  son compte
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Signal(Enum):
    """Les 3 seules décisions possibles d'un trader discipliné."""
    ACHAT = "ACHAT"
    VENTE = "VENTE"
    ATTENDRE = "ATTENDRE"  # Pas de signal = pas de trade. La discipline c'est aussi savoir attendre.


class ForceDuSignal(Enum):
    """Qualité du signal selon le nombre de confirmations."""
    FORT = "FORT"       # Tous les indicateurs sont alignés
    MOYEN = "MOYEN"     # Majorité des indicateurs confirment
    FAIBLE = "FAIBLE"   # Signal incertain - le trader gagnant attend


@dataclass
class AnalyseTendance:
    """Résultat de l'analyse de tendance selon la stratégie du suivi de tendance."""
    direction: str          # "HAUSSE", "BAISSE", "NEUTRE"
    ma20: float             # Moyenne mobile rapide (20 périodes)
    ma50: float             # Moyenne mobile lente (50 périodes)
    ma200: float            # Moyenne mobile long terme (200 périodes)
    pente_ma20: float       # Pente de la MA20 (positive = hausse)
    prix_au_dessus_ma50: bool


@dataclass
class AnalyseMomentum:
    """Analyse du momentum pour confirmer la tendance."""
    rsi: float              # RSI 14 - force du mouvement
    rsi_zone: str           # "SURVENTE", "NEUTRE", "SURACHAT"
    macd_signal: str        # "HAUSSIER", "BAISSIER", "NEUTRE"
    macd_valeur: float
    macd_signal_valeur: float
    macd_histogramme: float


@dataclass
class GestionRisque:
    """
    La règle d'or du trader gagnant : toujours définir son risque AVANT d'entrer.
    "Tout trader particulier qui se respecte sécurise ses positions" - Traders_Pro.pdf
    """
    prix_entree: float
    stop_loss: float        # Niveau où on coupe la perte - OBLIGATOIRE
    take_profit_1: float    # Premier objectif (1:2 risque/rendement)
    take_profit_2: float    # Deuxième objectif (1:3 risque/rendement)
    atr: float              # Average True Range - volatilité du marché
    risque_en_pips: float
    gain_potentiel_pips: float
    ratio_risque_rendement: float
    taille_position: float  # Lots à trader selon % de capital risqué
    capital_risque_pct: float  # % du capital risqué sur ce trade


@dataclass
class DecisionTrader:
    """
    La décision finale du cerveau du trader.
    Un bon trader ne prend une position QUE si tout est aligné.
    """
    signal: Signal
    force: ForceDuSignal
    paire: str
    timeframe: str
    prix_actuel: float

    # Analyse complète
    tendance: AnalyseTendance
    momentum: AnalyseMomentum
    gestion_risque: Optional[GestionRisque]

    # Score de confiance (0-100)
    score_confiance: int
    raisons: list[str]      # Pourquoi ce signal ?
    avertissements: list[str]  # Points d'attention

    # Citation du trader mind
    conseil_du_trader: str


class TraderBrain:
    """
    Le cerveau du trader - implémente les principes du livre Traders_Pro.pdf.

    "Le trader gagnant analyse le plus simplement du monde son graphique
    avec une méthode bien précise, afin de prendre les bonnes décisions."
    - Traders_Pro.pdf, Chapitre 5
    """

    # Paramètres du plan de trading (règles fixes - on ne dévie PAS)
    RISQUE_MAX_PAR_TRADE = 1.0      # Max 1% du capital par trade
    RATIO_RR_MINIMUM = 2.0          # Ratio Risque/Rendement minimum 1:2
    RSI_SURVENTE = 30               # Zone de survente
    RSI_SURACHAT = 70               # Zone de surachat
    RSI_NEUTRE_BAS = 45             # Limite basse de la zone neutre
    RSI_NEUTRE_HAUT = 55            # Limite haute de la zone neutre
    ATR_MULTIPLICATEUR_SL = 1.5     # Stop-loss = 1.5x ATR
    ATR_MULTIPLICATEUR_TP1 = 2.5    # TP1 = 2.5x ATR
    ATR_MULTIPLICATEUR_TP2 = 4.0    # TP2 = 4x ATR

    # Conseils du trader selon la situation
    CONSEILS = {
        Signal.ACHAT: [
            "La tendance est ton amie. Achète dans le sens du marché, pas contre lui.",
            "Signal d'achat confirmé. Pose ton stop-loss et laisse le trade travailler.",
            "Le marché monte. Entre avec discipline et respecte ton plan.",
        ],
        Signal.VENTE: [
            "La tendance est baissière. Vends dans le sens du courant.",
            "Signal de vente confirmé. Définis ton risque avant tout.",
            "Le marché baisse. Suis la tendance, c'est ta meilleure alliée.",
        ],
        Signal.ATTENDRE: [
            "Pas de signal clair. Le trader gagnant sait aussi NE PAS trader.",
            "Patience. Attendre un bon setup vaut mieux que trader n'importe comment.",
            "Le marché n'est pas clair. Préserve ton capital et attends la bonne occasion.",
        ],
    }

    def analyser_tendance(self, ma20: float, ma50: float, ma200: float,
                          prix: float, historique_ma20: list[float]) -> AnalyseTendance:
        """
        Analyse la tendance selon la stratégie du suivi de tendance.
        Principe PDF: "Acheter une devise à bas prix pour la revendre lorsque son prix est haut"
        """
        # Calcul de la pente de la MA20 (sur les 5 dernières valeurs)
        if len(historique_ma20) >= 5:
            pente = (historique_ma20[-1] - historique_ma20[-5]) / historique_ma20[-5] * 100
        else:
            pente = 0.0

        # Détermination de la direction
        if ma20 > ma50 > ma200 and pente > 0:
            direction = "HAUSSE"
        elif ma20 < ma50 < ma200 and pente < 0:
            direction = "BAISSE"
        elif ma20 > ma50 and pente > 0:
            direction = "HAUSSE"
        elif ma20 < ma50 and pente < 0:
            direction = "BAISSE"
        else:
            direction = "NEUTRE"

        return AnalyseTendance(
            direction=direction,
            ma20=ma20,
            ma50=ma50,
            ma200=ma200,
            pente_ma20=pente,
            prix_au_dessus_ma50=prix > ma50,
        )

    def analyser_momentum(self, rsi: float, macd: float,
                          macd_signal: float, macd_hist: float) -> AnalyseMomentum:
        """
        Analyse le momentum pour confirmer la tendance.
        Le RSI et le MACD sont des filtres - ils évitent d'entrer dans une zone épuisée.
        """
        # Zone RSI
        if rsi <= self.RSI_SURVENTE:
            rsi_zone = "SURVENTE"
        elif rsi >= self.RSI_SURACHAT:
            rsi_zone = "SURACHAT"
        else:
            rsi_zone = "NEUTRE"

        # Signal MACD
        if macd > macd_signal and macd_hist > 0:
            macd_sig = "HAUSSIER"
        elif macd < macd_signal and macd_hist < 0:
            macd_sig = "BAISSIER"
        else:
            macd_sig = "NEUTRE"

        return AnalyseMomentum(
            rsi=rsi,
            rsi_zone=rsi_zone,
            macd_signal=macd_sig,
            macd_valeur=macd,
            macd_signal_valeur=macd_signal,
            macd_histogramme=macd_hist,
        )

    def calculer_gestion_risque(self, signal: Signal, prix: float,
                                atr: float, capital: float,
                                decimales: int = 5) -> Optional[GestionRisque]:
        """
        Calcule le stop-loss, take-profit et taille de position.

        Principe PDF: "Contrôler et dimensionner ses positions afin de ne jamais
        perdre plus que ce qui est prévu par le plan de trading."
        """
        if signal == Signal.ATTENDRE:
            return None

        sl_distance = atr * self.ATR_MULTIPLICATEUR_SL
        tp1_distance = atr * self.ATR_MULTIPLICATEUR_TP1
        tp2_distance = atr * self.ATR_MULTIPLICATEUR_TP2

        if signal == Signal.ACHAT:
            stop_loss = prix - sl_distance
            take_profit_1 = prix + tp1_distance
            take_profit_2 = prix + tp2_distance
        else:  # VENTE
            stop_loss = prix + sl_distance
            take_profit_1 = prix - tp1_distance
            take_profit_2 = prix - tp2_distance

        risque_pips = abs(prix - stop_loss) * (10 ** (decimales - 1))
        gain_pips = abs(prix - take_profit_1) * (10 ** (decimales - 1))
        ratio_rr = gain_pips / risque_pips if risque_pips > 0 else 0

        # Taille de position: risquer max 1% du capital
        capital_risque = capital * (self.RISQUE_MAX_PAR_TRADE / 100)
        taille_position = round(capital_risque / (sl_distance * 100000), 2)

        return GestionRisque(
            prix_entree=round(prix, decimales),
            stop_loss=round(stop_loss, decimales),
            take_profit_1=round(take_profit_1, decimales),
            take_profit_2=round(take_profit_2, decimales),
            atr=round(atr, decimales),
            risque_en_pips=round(risque_pips, 1),
            gain_potentiel_pips=round(gain_pips, 1),
            ratio_risque_rendement=round(ratio_rr, 2),
            taille_position=taille_position,
            capital_risque_pct=self.RISQUE_MAX_PAR_TRADE,
        )

    def generer_signal(self, tendance: AnalyseTendance,
                       momentum: AnalyseMomentum) -> tuple[Signal, int, list[str], list[str]]:
        """
        Génère le signal final en combinant tendance + momentum.
        Le trader gagnant ne prend position QUE si les confirmations sont suffisantes.
        """
        score = 0
        raisons = []
        avertissements = []

        # --- ANALYSE DE TENDANCE (50 points max) ---
        if tendance.direction == "HAUSSE":
            score += 25
            raisons.append("Tendance haussière confirmée (MA20 > MA50)")
            if tendance.ma50 < tendance.ma200:
                # MA50 pas encore au-dessus MA200 - tendance moins sûre
                avertissements.append("MA50 toujours sous MA200 - tendance de fond baissière")
            else:
                score += 15
                raisons.append("Tendance long terme haussière (MA50 > MA200)")
            if tendance.pente_ma20 > 0.05:
                score += 10
                raisons.append("Pente MA20 positive - accélération haussière")

        elif tendance.direction == "BAISSE":
            score += 25
            raisons.append("Tendance baissière confirmée (MA20 < MA50)")
            if tendance.ma50 > tendance.ma200:
                avertissements.append("MA50 toujours au-dessus MA200 - tendance de fond haussière")
            else:
                score += 15
                raisons.append("Tendance long terme baissière (MA50 < MA200)")
            if tendance.pente_ma20 < -0.05:
                score += 10
                raisons.append("Pente MA20 négative - accélération baissière")
        else:
            avertissements.append("Tendance neutre/indécise - marché sans direction claire")

        # --- ANALYSE MOMENTUM (50 points max) ---
        # RSI
        if tendance.direction == "HAUSSE":
            if self.RSI_NEUTRE_BAS <= momentum.rsi <= self.RSI_SURACHAT - 10:
                score += 20
                raisons.append(f"RSI favorable pour achat ({momentum.rsi:.1f})")
            elif momentum.rsi <= self.RSI_SURVENTE:
                score += 15
                raisons.append(f"RSI en survente ({momentum.rsi:.1f}) - rebond possible")
            elif momentum.rsi >= self.RSI_SURACHAT:
                score -= 10
                avertissements.append(f"RSI en surachat ({momentum.rsi:.1f}) - risque de correction")

        elif tendance.direction == "BAISSE":
            if self.RSI_SURVENTE + 10 <= momentum.rsi <= self.RSI_NEUTRE_HAUT:
                score += 20
                raisons.append(f"RSI favorable pour vente ({momentum.rsi:.1f})")
            elif momentum.rsi >= self.RSI_SURACHAT:
                score += 15
                raisons.append(f"RSI en surachat ({momentum.rsi:.1f}) - baisse possible")
            elif momentum.rsi <= self.RSI_SURVENTE:
                score -= 10
                avertissements.append(f"RSI en survente ({momentum.rsi:.1f}) - risque de rebond")

        # MACD
        if tendance.direction == "HAUSSE" and momentum.macd_signal == "HAUSSIER":
            score += 20
            raisons.append("MACD haussier - momentum confirmé")
        elif tendance.direction == "BAISSE" and momentum.macd_signal == "BAISSIER":
            score += 20
            raisons.append("MACD baissier - momentum confirmé")
        elif momentum.macd_signal == "NEUTRE":
            avertissements.append("MACD neutre - momentum incertain")

        # Prix par rapport à MA50
        if tendance.direction == "HAUSSE" and tendance.prix_au_dessus_ma50:
            score += 10
            raisons.append("Prix au-dessus de la MA50 - zone haussière")
        elif tendance.direction == "BAISSE" and not tendance.prix_au_dessus_ma50:
            score += 10
            raisons.append("Prix en-dessous de la MA50 - zone baissière")

        # --- DÉCISION FINALE ---
        score = max(0, min(100, score))

        if score >= 60 and tendance.direction == "HAUSSE":
            signal = Signal.ACHAT
        elif score >= 60 and tendance.direction == "BAISSE":
            signal = Signal.VENTE
        else:
            signal = Signal.ATTENDRE
            if tendance.direction == "NEUTRE":
                raisons.append("Marché sans tendance claire - on attend")
            else:
                raisons.append(f"Score de confiance insuffisant ({score}/100) - on attend")

        return signal, score, raisons, avertissements

    def analyser(self, paire: str, timeframe: str, prix: float,
                 ma20: float, ma50: float, ma200: float,
                 historique_ma20: list[float],
                 rsi: float, macd: float, macd_signal_val: float, macd_hist: float,
                 atr: float, capital: float = 1000.0,
                 decimales: int = 5) -> DecisionTrader:
        """
        Point d'entrée principal - analyse complète selon les principes du PDF.
        Retourne une décision complète avec tous les niveaux de prix.
        """
        import random

        tendance = self.analyser_tendance(ma20, ma50, ma200, prix, historique_ma20)
        momentum = self.analyser_momentum(rsi, macd, macd_signal_val, macd_hist)
        signal, score, raisons, avertissements = self.generer_signal(tendance, momentum)

        # Force du signal
        if score >= 80:
            force = ForceDuSignal.FORT
        elif score >= 60:
            force = ForceDuSignal.MOYEN
        else:
            force = ForceDuSignal.FAIBLE

        gestion = self.calculer_gestion_risque(signal, prix, atr, capital, decimales)

        # Vérification ratio R/R minimum
        if gestion and gestion.ratio_risque_rendement < self.RATIO_RR_MINIMUM:
            signal = Signal.ATTENDRE
            force = ForceDuSignal.FAIBLE
            avertissements.append(
                f"Ratio R/R insuffisant ({gestion.ratio_risque_rendement:.1f}) - "
                f"minimum requis: {self.RATIO_RR_MINIMUM}"
            )
            gestion = None

        conseil = random.choice(self.CONSEILS[signal])

        return DecisionTrader(
            signal=signal,
            force=force,
            paire=paire,
            timeframe=timeframe,
            prix_actuel=prix,
            tendance=tendance,
            momentum=momentum,
            gestion_risque=gestion,
            score_confiance=score,
            raisons=raisons,
            avertissements=avertissements,
            conseil_du_trader=conseil,
        )
