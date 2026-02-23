"""
Récupération des données de marché Forex via yfinance.
Le Forex est recommandé pour les débutants selon Traders_Pro.pdf :
- Marché ouvert 24h/24
- Accessible avec peu de fonds
- Liquidité maximale
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


# Paires Forex disponibles (symboles Yahoo Finance)
PAIRES_FOREX = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "USD/CHF": "USDCHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
}

# Indices boursiers
INDICES = {
    "CAC 40":     "^FCHI",
    "NASDAQ":     "^IXIC",
    "S&P 500":    "^GSPC",
    "DAX":        "^GDAXI",
    "DOW JONES":  "^DJI",
}

# Matières premières (commodities)
COMMODITIES = {
    "OR":     "GC=F",
    "PÉTROLE": "CL=F",
}

TOUS_LES_MARCHES = {**PAIRES_FOREX, **INDICES, **COMMODITIES}

# Timeframes disponibles
TIMEFRAMES = {
    "1h":   ("1h",  "60d"),
    "4h":   ("1h",  "60d"),   # yfinance n'a pas de 4h direct, on rééchantillonne
    "1j":   ("1d",  "1y"),
    "1sem": ("1wk", "5y"),
}


def telecharger_donnees(symbole_yf: str, intervalle: str = "1d",
                        periode: str = "1y") -> pd.DataFrame:
    """
    Télécharge les données OHLCV pour un symbole donné.
    Retourne un DataFrame avec: Open, High, Low, Close, Volume
    """
    ticker = yf.Ticker(symbole_yf)
    df = ticker.history(period=periode, interval=intervalle)

    if df.empty:
        raise ValueError(f"Impossible de récupérer les données pour {symbole_yf}")

    df.index = pd.to_datetime(df.index)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.dropna()

    return df


def get_prix_actuel(nom_paire: str) -> float:
    """Retourne le prix actuel d'une paire."""
    symbole = TOUS_LES_MARCHES.get(nom_paire)
    if not symbole:
        raise ValueError(f"Paire inconnue: {nom_paire}")

    ticker = yf.Ticker(symbole)
    info = ticker.fast_info
    return round(float(info.last_price), 5)


def get_donnees_paire(nom_paire: str, timeframe: str = "1j") -> pd.DataFrame:
    """
    Interface principale: retourne les données pour une paire et un timeframe.
    Gère le rééchantillonnage pour les timeframes non supportés nativement.
    """
    symbole = TOUS_LES_MARCHES.get(nom_paire)
    if not symbole:
        raise ValueError(f"Marché inconnu: {nom_paire}")

    intervalle, periode = TIMEFRAMES.get(timeframe, ("1d", "1y"))
    df = telecharger_donnees(symbole, intervalle, periode)

    # Rééchantillonnage 4h (yfinance ne supporte pas 4h directement)
    if timeframe == "4h":
        df = df.resample("4h").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }).dropna()

    return df


def lister_marches() -> dict:
    """Retourne tous les marchés disponibles organisés par catégorie."""
    return {
        "Forex (Recommandé pour débuter)": list(PAIRES_FOREX.keys()),
        "Indices Boursiers": list(INDICES.keys()),
        "Matières Premières": list(COMMODITIES.keys()),
    }
