# TRADER PRO — Cerveau du Trader
> Ce fichier est la mémoire de l'application. Toute la logique du `traderBrain()` est dérivée de ces règles.
> Source : "Les secrets des traders particuliers qui gagnent" + Reversal Patterns PDF + méthode Extreme Money (niveaux clés)

---

## 1. Philosophie de base

- **Suivre la tendance** : ne jamais trader contre le courant dominant
- **Score de confiance 0–100** avant chaque décision
- **R/R minimum 1:2** : si le risque/rendement est insuffisant → ATTENDRE
- **Préserver le capital** : pas de signal clair = pas de trade

---

## 2. Détection de tendance (Moyennes Mobiles)

| Condition | Direction |
|-----------|-----------|
| MA20 > MA50 + pente MA20 positive | HAUSSE |
| MA20 < MA50 + pente MA20 négative | BAISSE |
| Autre | NEUTRE |

- **MA50 > MA200** → tendance long terme haussière (+15 pts)
- **MA50 < MA200** → tendance long terme baissière (warning si on achète)
- **Pente MA20 > 0.05%** → accélération (+10 pts)

---

## 3. Confirmation momentum

### RSI 14
| Valeur RSI | Signal | Score |
|------------|--------|-------|
| 45–60 en hausse | Favorable achat | +20 |
| ≤ 30 en hausse | Survente → rebond | +15 |
| ≥ 70 en hausse | Surachat → risque correction | -10 |
| 40–55 en baisse | Favorable vente | +20 |
| ≥ 70 en baisse | Surachat → baisse probable | +15 |
| ≤ 30 en baisse | Survente → risque rebond | -10 |

### MACD (12/26/9)
- **MACD > Signal + Histogramme > 0** → momentum haussier (+20 si aligné)
- **MACD < Signal + Histogramme < 0** → momentum baissier (+20 si aligné)
- Non aligné → warning

---

## 4. Patterns de Retournement Japonais (Reversal Patterns)

> Source : Reversal Patterns PDF — classés par fiabilité

### Haussiers — Haute fiabilité (+20 pts si confirmé)
- **Three White Soldiers** : 3 bougies haussières consécutives, chacune fermant plus haut
- **Three Inside Up** : grande baissière → petite haussière intérieure → haussière cassant au-dessus
- **Three Outside Up** : englobe baissier puis confirmation haussière
- **Morning Doji Star** : baissière + doji + grande haussière
- **Abandoned Baby** : gap + doji isolé + gap inverse

### Haussiers — Fiabilité moyenne (+10 pts)
- **Bullish Engulfing** : la bougie haussière englobe complètement la baissière précédente
- **Morning Star** : baissière (grande) + petite + haussière (grande) au-dessus du milieu
- **Piercing Line** : ouvre sous le bas précédent, ferme au-dessus du milieu de la baissière
- **Hammer** : corps en haut, mèche inférieure ≥ 2× le corps, peu de mèche haute
- **Dragonfly Doji** : ouverture ≈ fermeture ≈ haut, longue mèche inférieure

### Haussiers — Faible fiabilité (+5 pts)
- **Inverted Hammer** : corps en bas, longue mèche haute
- **Harami Haussier** : petite bougie haussière à l'intérieur d'une grande baissière
- **Tweezers Bottom** : deux bougies avec même bas

### Baissiers — Haute fiabilité (+20 pts si confirmé)
- **Evening Star** : haussière (grande) + petite + baissière (grande) sous le milieu
- **Dark Cloud Cover** : ouvre au-dessus du haut précédent, ferme sous le milieu de la haussière
- **Three Inside Down** : grande haussière → petite baissière intérieure → baissière cassant en-dessous
- **Three Outside Down** : englobant haussier puis confirmation baissière
- **Evening Doji Star** : haussière + doji + grande baissière

### Baissiers — Fiabilité moyenne (+10 pts)
- **Bearish Engulfing** : la bougie baissière englobe complètement la haussière précédente
- **Hanging Man** : corps en haut, longue mèche inférieure, en haut d'une tendance haussière
- **Shooting Star** : corps en bas, longue mèche haute ≥ 2× corps, peu de mèche basse
- **Gravestone Doji** : ouverture ≈ fermeture ≈ bas, longue mèche haute

### Baissiers — Faible fiabilité (+5 pts)
- **Harami Baissier** : petite bougie baissière à l'intérieur d'une grande haussière
- **Tweezers Top** : deux bougies avec même haut

---

## 5. Niveaux Support/Résistance Clés (méthode Extreme Money)

> Basé sur la méthode de la chaîne YouTube @tradingformation4371 (Extreme Money)

### Principe fondamental
Le prix **respecte** les niveaux ouverts des grandes périodes. Ces niveaux sont magnétiques.

### Niveaux à surveiller (par ordre d'importance)
1. **Monthly Open** (ouverture du mois) — niveau le plus puissant
2. **Monthly High/Low** (extrêmes du mois courant) — résistance/support fort
3. **Previous Month High/Low** (extrêmes du mois précédent) — zones clés
4. **Weekly Open** (ouverture de la semaine) — niveau fort
5. **Weekly High/Low** (extrêmes de la semaine courante)
6. **Previous Week High/Low** — zones de retournement fréquentes
7. **Daily High/Low** (extrêmes de la veille) — niveaux intraday

### Règles d'utilisation
- **BUY** : chercher à acheter SUR un support (Monthly Open, Weekly Low, etc.)
- **SELL** : chercher à vendre SUR une résistance (Monthly High, Weekly High, etc.)
- **Prix proche d'un niveau (±0.5 ATR)** : +5 à +10 pts au score de confiance
- **Prix entre deux niveaux sans direction** → ATTENDRE

### Calcul depuis les données OHLC
- Monthly Open = ouverture de la 1ère bougie du mois courant
- Weekly Open = ouverture du lundi de la semaine courante
- Ces valeurs sont extraites des bougies journalières ou horaires

---

## 6. Calcul du Risk Management

```
SL = prix ± (ATR × 1.5)
TP1 = prix ± (ATR × 2.5)   → R/R = 1:1.67
TP2 = prix ± (ATR × 4.0)   → R/R = 1:2.67
Lots = Capital × Risque% ÷ (SL_pips × PipValue)
```

- Si R/R TP1 < 2.0 → signal = ATTENDRE
- Lots = arrondi au centième inférieur

---

## 7. Score de confiance — Récapitulatif

| Critère | Max |
|---------|-----|
| Tendance (MA20/50) | +25 |
| Long terme (MA50/200) | +15 |
| Pente MA20 | +10 |
| RSI favorable | +20 |
| MACD aligné | +20 |
| Prix / MA50 | +10 |
| Reversal pattern haute fiabilité | +20 |
| Reversal pattern fiabilité moyenne | +10 |
| Reversal pattern faible | +5 |
| Niveau support/résistance clé | +10 |
| **TOTAL MAX** | **135** (ramené à 100) |

Signal **ACHAT** si score ≥ 60 + direction = HAUSSE
Signal **VENTE** si score ≥ 60 + direction = BAISSE
Sinon **ATTENDRE**

---

## 8. Résumé verdict (affiché dans l'app)

Le verdict doit répondre à 3 questions :
1. **Quelle est la tendance ?** (haussière/baissière/neutre)
2. **Y a-t-il un pattern de confirmation ?** (reversal ou continuation)
3. **Le prix est-il sur un niveau clé ?** (support/résistance)

Si ≥ 2/3 → signal, sinon → ATTENDRE
