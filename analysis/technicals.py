"""
Indicateurs techniques - les "armes" du trader selon Traders_Pro.pdf.

Les 4 indicateurs indispensables mentionnés dans le PDF :
1. Moyennes Mobiles (MA20, MA50, MA200) - détection de tendance
2. RSI - force du mouvement, zones de surachat/survente
3. MACD - confirmation de momentum
4. ATR - mesure de la volatilité pour le stop-loss
"""

import pandas as pd
import numpy as np


def calculer_moyenne_mobile(serie: pd.Series, periode: int) -> pd.Series:
    """Moyenne mobile simple (SMA)."""
    return serie.rolling(window=periode).mean()


def calculer_ema(serie: pd.Series, periode: int) -> pd.Series:
    """Moyenne mobile exponentielle (EMA) - réagit plus vite aux changements."""
    return serie.ewm(span=periode, adjust=False).mean()


def calculer_rsi(serie: pd.Series, periode: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI) - mesure la force d'un mouvement.
    - RSI > 70 : surachat (risque de retournement)
    - RSI < 30 : survente (rebond possible)
    - RSI entre 40-60 : zone neutre
    """
    delta = serie.diff()
    gain = delta.clip(lower=0)
    perte = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=periode - 1, min_periods=periode).mean()
    avg_perte = perte.ewm(com=periode - 1, min_periods=periode).mean()

    rs = avg_gain / avg_perte.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def calculer_macd(serie: pd.Series,
                  rapide: int = 12,
                  lent: int = 26,
                  signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD (Moving Average Convergence Divergence).
    Retourne: (macd_line, signal_line, histogramme)

    Croisement MACD > Signal → signal haussier
    Croisement MACD < Signal → signal baissier
    """
    ema_rapide = calculer_ema(serie, rapide)
    ema_lente = calculer_ema(serie, lent)
    macd_line = ema_rapide - ema_lente
    signal_line = calculer_ema(macd_line, signal)
    histogramme = macd_line - signal_line
    return macd_line, signal_line, histogramme


def calculer_atr(df: pd.DataFrame, periode: int = 14) -> pd.Series:
    """
    Average True Range (ATR) - mesure la volatilité.
    Utilisé pour placer le stop-loss à une distance cohérente avec le marché.
    "Ne jamais perdre plus que ce qui est prévu" - Traders_Pro.pdf
    """
    high = df["high"]
    low = df["low"]
    close_precedent = df["close"].shift(1)

    tr1 = high - low
    tr2 = (high - close_precedent).abs()
    tr3 = (low - close_precedent).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.ewm(com=periode - 1, min_periods=periode).mean()
    return atr


def calculer_bollinger(serie: pd.Series, periode: int = 20,
                       nb_ecarts: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bandes de Bollinger - zones de support/résistance dynamiques.
    Retourne: (bande_haute, moyenne, bande_basse)
    """
    moyenne = calculer_moyenne_mobile(serie, periode)
    ecart_type = serie.rolling(window=periode).std()
    bande_haute = moyenne + (ecart_type * nb_ecarts)
    bande_basse = moyenne - (ecart_type * nb_ecarts)
    return bande_haute, moyenne, bande_basse


def calculer_stochastique(df: pd.DataFrame,
                          periode_k: int = 14,
                          periode_d: int = 3) -> tuple[pd.Series, pd.Series]:
    """
    Oscillateur stochastique - confirme les zones de retournement.
    Retourne: (ligne_k, ligne_d)
    """
    lowest_low = df["low"].rolling(window=periode_k).min()
    highest_high = df["high"].rolling(window=periode_k).max()

    k = 100 * ((df["close"] - lowest_low) / (highest_high - lowest_low).replace(0, np.nan))
    d = k.rolling(window=periode_d).mean()
    return k.fillna(50), d.fillna(50)


def ajouter_tous_les_indicateurs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule et ajoute tous les indicateurs techniques au DataFrame.
    C'est la "boîte à outils" complète du trader.
    """
    df = df.copy()
    close = df["close"]

    # Moyennes Mobiles
    df["ma20"] = calculer_moyenne_mobile(close, 20)
    df["ma50"] = calculer_moyenne_mobile(close, 50)
    df["ma200"] = calculer_moyenne_mobile(close, 200)
    df["ema9"] = calculer_ema(close, 9)
    df["ema21"] = calculer_ema(close, 21)

    # Momentum
    df["rsi"] = calculer_rsi(close, 14)
    df["macd"], df["macd_signal"], df["macd_hist"] = calculer_macd(close)

    # Volatilité
    df["atr"] = calculer_atr(df, 14)
    df["atr_pct"] = (df["atr"] / close * 100).round(3)  # ATR en % du prix

    # Bollinger
    df["bb_haute"], df["bb_moy"], df["bb_basse"] = calculer_bollinger(close)

    # Stochastique
    df["stoch_k"], df["stoch_d"] = calculer_stochastique(df)

    # Suppression des lignes avec NaN (début de série insuffisant)
    df = df.dropna(subset=["ma200", "macd", "rsi"])

    return df


def extraire_valeurs_actuelles(df: pd.DataFrame) -> dict:
    """
    Extrait les valeurs actuelles (dernière bougie) de tous les indicateurs.
    C'est ce que "lit" le cerveau du trader pour prendre sa décision.
    """
    derniere = df.iloc[-1]
    historique_ma20 = df["ma20"].dropna().tolist()

    return {
        "prix": float(derniere["close"]),
        "open": float(derniere["open"]),
        "high": float(derniere["high"]),
        "low": float(derniere["low"]),
        "ma20": float(derniere["ma20"]),
        "ma50": float(derniere["ma50"]),
        "ma200": float(derniere["ma200"]),
        "ema9": float(derniere["ema9"]),
        "ema21": float(derniere["ema21"]),
        "rsi": float(derniere["rsi"]),
        "macd": float(derniere["macd"]),
        "macd_signal": float(derniere["macd_signal"]),
        "macd_hist": float(derniere["macd_hist"]),
        "atr": float(derniere["atr"]),
        "atr_pct": float(derniere["atr_pct"]),
        "bb_haute": float(derniere["bb_haute"]),
        "bb_basse": float(derniere["bb_basse"]),
        "stoch_k": float(derniere["stoch_k"]),
        "stoch_d": float(derniere["stoch_d"]),
        "historique_ma20": historique_ma20[-10:],
        "date": str(df.index[-1]),
        "nb_bougies": len(df),
    }
