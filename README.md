# Trader Pro — Analyseur de trading Forex

Application Python en ligne de commande qui analyse les marchés Forex
selon les principes du livre "Les secrets des traders particuliers qui gagnent".

## Prérequis

- Python 3.10 ou plus récent
- pip

## Installation

```bash
git clone https://github.com/franckyCHR/trader-pro.git
cd trader-pro
pip3 install -r requirements.txt
```

## Utilisation

```bash
# Mode interactif (menu complet)
python3 main.py

# Analyser une paire directement
python3 main.py --paire EUR/USD --timeframe 1j --capital 1000

# Scanner toutes les paires Forex
python3 main.py --scan --timeframe 1j

# Lister les marchés disponibles
python3 main.py --liste
```

## Structure

```
trader_pro/
├── main.py                  ← Point d'entrée
├── requirements.txt         ← Dépendances Python
├── brain/
│   └── trader_mind.py       ← Cerveau : logique du trader gagnant
├── data/
│   └── market_data.py       ← Données Forex en temps réel (yfinance)
├── analysis/
│   └── technicals.py        ← Indicateurs : MA, RSI, MACD, ATR
└── display/
    └── dashboard.py         ← Interface terminal (Rich)
```

## Marchés supportés

- **Forex** : EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD...
- **Indices** : CAC 40, NASDAQ, S&P 500, DAX, Dow Jones
- **Matières premières** : Or, Pétrole

## Principes intégrés (Traders_Pro.pdf)

1. Suivi de tendance (MA20 / MA50 / MA200)
2. Confirmation momentum (RSI + MACD)
3. Gestion du risque automatique (Stop-Loss via ATR)
4. Ratio Risque/Rendement minimum 1:2
5. Score de confiance 0-100 avant chaque décision
