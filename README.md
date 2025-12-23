# Mesure et gestion du risque des portefeuilles OPCVM à l’aide de la Data Science


## **Description du projet**

Le secteur de la gestion d’actifs, et en particulier celui des OPCVM (Organismes de Placement Collectif en Valeurs Mobilières), est confronté à des défis majeurs en matière de **gestion du risque financier**. Les risques de marché, de liquidité et de volatilité peuvent impacter significativement la performance des fonds et, par conséquent, les intérêts des investisseurs. De plus, les méthodes traditionnelles d’évaluation du risque (VaR, CVaR, volatilité historique) peuvent s’avérer insuffisantes pour anticiper des événements extrêmes ou des corrélations dynamiques entre actifs.

Ce projet a pour objectif de **développer une approche data-driven pour mesurer, prédire et gérer le risque d’un portefeuille OPCVM**, en exploitant les techniques avancées de la Data Science et de l’intelligence artificielle. Plus spécifiquement, le projet vise à **Estimer précisément la volatilité sur 2 semaines** de l'**OPCVM Attijari diversifié** portefeuille, en combinant méthodes classiques GARCH, volatilité historique, et modèles d’apprentissage automatique (Random Forests, XGBoost) pour anticiper les fluctuations futures du fond.


Ce projet représente une opportunité concrète de **moderniser la gestion du risque dans les OPCVM** en intégrant l’analyse avancée de données et la prévision des risques financiers, tout en améliorant la prise de décision et la transparence pour les investisseurs.

## **Quelques définitions**


- Un **OPCVM** (Organisme de Placement Collectif en Valeurs Mobilières) est un fonds qui permet à plusieurs investisseurs de **mettre en commun leur argent** pour qu’un gestionnaire professionnel investisse ce capital dans un **panier diversifié de titres financiers** (actions, obligations, etc.). L’objectif est de **diversifier le risque** et de **faciliter l’accès aux marchés financiers** pour les particuliers.
- **Attijari Diversifié** est un **OPCVM** géré par Attijariwafa Bank qui investit dans un **panier varié d’instruments financiers** (actions, obligations, et autres actifs) afin de **diversifier le risque** et chercher un **équilibre entre rendement et sécurité** pour les investisseurs.
- **Risque de marché**: le risque de marché correspond à la **perte potentielle due aux variations des prix des actifs financiers** dans le portefeuille, comme les actions, obligations ou devises. C’est le risque lié aux **mouvements généraux** du marché.
- **Risque de liquidité**: Le risque de liquidité correspond à la **difficulté de vendre un actif rapidement sans affecter son prix.** Il devient critique si l’OPCVM doit rembourser des investisseurs mais que certains actifs ne peuvent pas être liquidés facilement.
- **Volatilité**: La volatilité mesure la **dispersion des rendements autour de leur moyenne.** Plus la volatilité est élevée → plus le portefeuille est risqué.
- **Risque de volatilité**: Le risque de volatilité correspond à la **grande variation des prix d’un actif ou d’un portefeuille sur une période donnée.** Une forte volatilité augmente l’incertitude sur le rendement futur.




## Architecture globale du projet

```
┌─────────────────────────────────────────────────────────────────┐
│                  ACQUISITION (SCRAPING)                         │
├─────────────────────────────────────────────────────────────────┤
│ Investing.com (MASI)  →  weekly_masi_scraper  →  CSV weekly     │
│ Wafa Gestion (OPCVM)  →  weekly_opcvm_scraper  →  CSV weekly    │
│ Import manuel (Historique)  →  Moroccan All Shares.csv          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  NETTOYAGE (CLEANING)                           │
├─────────────────────────────────────────────────────────────────┤
│ dataset_cleaning.ipynb                                          │
│ → MASI_cleaned.csv                                              │
│ → attijari_diversifie.csv                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              TRANSFORMATION & FEATURES (PROCESSING)             │
├─────────────────────────────────────────────────────────────────┤
│ dataset_processing.py                                           │
│ 1. Fusion MASI quotidien + hebdomadaire                         │
│ 2. Calcul GARCH volatility                                      │
│ 3. Feature engineering (lags, performances)                     │
│ → final_dataset.csv (prêt pour ML)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              MODÉLISATION (ML TRAINING)                         │
├─────────────────────────────────────────────────────────────────┤
│ modelling.py                                                    │
│ Algo: Dynamic Forecast with XGBoost Retraining                  │
│ Target: vol_future_2w (volatilité 2 semaines)                   │
│ → volatility_forecasted_dataset.csv                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  API (BACKEND FASTAPI)                          │
├─────────────────────────────────────────────────────────────────┤
│ backend/main.py                                                 │
│ Endpoints:                                                      │
│ GET  /api/final/opcvm_liquidative         → Valeur Liquidative  │
│ GET  /api/final/masi_weekly_mean          → MASI hebdo          │
│ POST /api/volatility/run-modelling        → Lance modelling.py  │
│ GET  /api/volatility/forecast             → Dernière prédiction │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              DASHBOARD (FRONTEND NEXT.JS)                       │
├─────────────────────────────────────────────────────────────────┤
│ react-financial-app/                                            │
│ • Affichage des séries temporelles (MASI, OPCVM)                │
│ • Graphiques Recharts (données hebdomadaires)                   │
│ • Bouton "Prédire la volatilité" → appel /run-modelling         │
│ • Affichage des prédictions XGBoost                             │
│ • Vue: Financial Dashboard (Vercel URL)                         │
└─────────────────────────────────────────────────────────────────┘
```

**Résultats approche ML**

**Résultats approche Traditionnel Garch**



**Comparaison**

Les résultats montrent que le modèle de forecast dynamique **surpasse largement le GARCH** :

* RMSE : 0.0052 contre 0.0104
* MAE  : 0.0034 contre 0.0086
* R²   : 0.3910 contre -1.3655

Ces indicateurs montrent que le modèle prédit **plus précisément la volatilité future** et capture mieux la variation des données, contrairement au GARCH dont les prédictions sont moins fiables et moins adaptées à ce dataset.




