# Mesure et gestion du risque des portefeuilles OPCVM à l’aide de la Data Science


## **Description du projet**

Le secteur de la gestion d’actifs, et en particulier celui des OPCVM (Organismes de Placement Collectif en Valeurs Mobilières), est confronté à des défis majeurs en matière de **gestion du risque financier**. Les risques de marché, de liquidité et de volatilité peuvent impacter significativement la performance des fonds et, par conséquent, les intérêts des investisseurs. De plus, les méthodes traditionnelles d’évaluation du risque (VaR, CVaR, volatilité historique) peuvent s’avérer insuffisantes pour anticiper des événements extrêmes ou des corrélations dynamiques entre actifs.

Ce projet a pour objectif de **développer une approche data-driven pour mesurer, prédire et gérer le risque d’un portefeuille OPCVM**, en exploitant les techniques avancées de la Data Science et de l’intelligence artificielle. Plus spécifiquement, le projet vise à :

1. **Estimer précisément la volatilité et le risque** du portefeuille, en combinant méthodes classiques (GARCH, volatilité historique) et modèles d’apprentissage automatique (LSTM, Transformers, Random Forests, XGBoost) pour anticiper les fluctuations futures des actifs.
2. **Analyser les corrélations dynamiques entre actifs**, afin d’identifier les dépendances temporelles et les risques de concentration qui peuvent affecter le portefeuille dans des conditions de marché variées.
3. **Réaliser des stress tests sur des scénarios extrêmes**, en simulant des mouvements de marché sévères via Monte Carlo ou modèles génératifs, afin d’évaluer la vulnérabilité du portefeuille et de proposer des mesures préventives.

Le projet combine ainsi des méthodes statistiques, des algorithmes de Machine Learning et des techniques de simulation pour produire **des indicateurs de risque fiables**, applicables aux décisions de gestion de portefeuille. Les livrables attendus incluent :

* Des métriques de risque améliorées (VaR, CVaR, volatilité prédite),
* Des visualisations dynamiques des corrélations et de la distribution des risques,
* Un rapport de stress testing détaillé,
* Un tableau de bord interactif permettant de suivre en temps réel l’évolution du risque.

Ce projet représente une opportunité concrète de **moderniser la gestion du risque dans les OPCVM** en intégrant l’analyse avancée de données et la prévision des risques financiers, tout en améliorant la prise de décision et la transparence pour les investisseurs.

## **Quelques définitions**

- **Risque de marché**: le risque de marché correspond à la **perte potentielle due aux variations des prix des actifs financiers** dans le portefeuille, comme les actions, obligations ou devises. C’est le risque lié aux **mouvements généraux** du marché.
- **Risque de liquidité**: Le risque de liquidité correspond à la **difficulté de vendre un actif rapidement sans affecter son prix.** Il devient critique si l’OPCVM doit rembourser des investisseurs mais que certains actifs ne peuvent pas être liquidés facilement.
- **Risque de volatilité**: Le risque de volatilité correspond à la **grande variation des prix d’un actif ou d’un portefeuille sur une période donnée.** Une forte volatilité augmente l’incertitude sur le rendement futur.
- **VaR – Value at Risk**: La VaR mesure la **perte maximale qu’un portefeuille pourrait subir sur une période donnée, avec un certain niveau de confiance.**
- **CVaR – Conditional Value at Risk**: Le CVaR complète la VaR. Il mesure la **perte moyenne dans le pire X % des cas.**
- **Volatilité**: La volatilité mesure la **dispersion des rendements autour de leur moyenne.** Plus la volatilité est élevée → plus le portefeuille est risqué.


## Passages importants

*Bien que les rendements soient observés quotidiennement, la volatilité est une variable latente estimée à une fréquence journalière à partir des rendements passés, reflétant l’incertitude associée aux variations futures des prix.*   

*La Value at Risk (VaR) mesure la perte maximale attendue à un niveau de confiance donné, tandis que la Conditional Value at Risk (CVaR) évalue la perte moyenne conditionnelle aux pires scénarios. La combinaison des deux indicateurs permet une évaluation plus complète du risque de portefeuille, en particulier dans les périodes de stress.*    

*Les modèles GARCH et EGARCH sont utilisés pour estimer la volatilité conditionnelle des rendements financiers. Tandis que GARCH capture la persistance de la volatilité, EGARCH permet de modéliser l’asymétrie des chocs de marché, les pertes ayant un impact plus important que les gains sur la volatilité future.*   

*Une approche hybride combinant les modèles classiques GARCH/EGARCH avec des modèles de Machine Learning permet d’estimer de manière plus précise la volatilité et le risque d’un portefeuille. Les modèles classiques capturent la persistance et la dynamique historique des rendements, tandis que les modèles ML corrigent les limites de structure et capturent les relations complexes non-linéaires, conduisant à des mesures de risque (VaR et CVaR) plus fiables.*

*Dans l’approche hybride A, la volatilité estimée par GARCH/EGARCH est utilisée comme feature principale dans un modèle de Machine Learning ou Deep Learning. Le modèle apprend à prédire la volatilité future, qui est ensuite utilisée pour calculer des mesures de risque telles que la VaR et la CVaR, combinant ainsi la robustesse des modèles classiques et la flexibilité du ML.*   

*Pour l’étude empirique, nous sélectionnons l’OPCVM Attijari Diversifié géré par Wafa Gestion, un fonds multi‑actifs représentatif de la classe diversifiée au Maroc. Ce fonds sera analysé en termes de volatilité, de risques extrêmes (VaR/CVaR) et de dépendances temporelles entre ses composantes, à l’aide de méthodes classiques (GARCH/EGARCH) et modernes (Machine Learning).*


## Axes scientifiques clés du projet

Ton projet repose sur **4 piliers techniques majeurs** :

### 🔹 Axe 1 : Mesure et prévision de la volatilité

> *“À quel point le portefeuille est instable aujourd’hui et demain ?”*

* Méthodes classiques :

  * Volatilité historique
  * GARCH / EGARCH
* Méthodes ML / DL :

  * LSTM (séries temporelles financières)
  * Transformers (attention sur long terme)
  * Random Forest / XGBoost (features techniques)

🎯 **Sorties attendues** :

* Volatilité prédite
* VaR / CVaR dynamiques
* Comparaison classique vs ML

---

### 🔹 Axe 2 : Corrélations dynamiques entre actifs

> *“Quels actifs deviennent dangereux ensemble dans certaines conditions ?”*

* Problème clé :

  * Les corrélations **ne sont pas constantes**
* Méthodes possibles :

  * Rolling correlation
  * DCC-GARCH
  * PCA dynamique
  * Graphes de corrélation (network analysis)

🎯 **Sorties attendues** :

* Heatmaps temporelles
* Graphes de dépendance
* Détection des risques de concentration

---

### 🔹 Axe 3 : Stress testing et scénarios extrêmes

> *“Que se passe-t-il si le marché s’effondre ?”*

* Techniques :

  * Monte Carlo simulation
  * Scénarios historiques (crise 2008, Covid, etc.)
  * Modèles génératifs (optionnel, bonus)
* Analyse :

  * pertes extrêmes
  * VaR conditionnelle
  * drawdown maximal

🎯 **Sorties attendues** :

* Rapports de stress tests
* Distributions de pertes
* Comparaison normal vs stressé

---

### 🔹 Axe 4 : Visualisation & dashboard

> *“Comment rendre le risque lisible pour un gestionnaire ?”*

* Tableaux de bord interactifs :

  * évolution de la VaR
  * volatilité prédite
  * corrélations
* Outils :

  * Streamlit / Dash / Power BI

🎯 **Sorties attendues** :

* Dashboard temps réel (ou quasi)
* Visualisations claires pour décision

---

## Architecture globale du projet

Voici une **architecture logique** (très appréciée par les jurys 👇)

```
Données financières (Prix journaliers / VL du fonds)
        ↓
Calcul des rendements journaliers
        ↓
Prétraitement & Feature Engineering
        - Rendements passés
        - Volatilité GARCH / EGARCH
        - Indicateurs macro (optionnel)
        ↓
┌────────────────────────────┐
│  Modèles de volatilité     │
│  - GARCH / EGARCH          │
│  - ML / DL (LSTM, XGBoost,│
│    Transformers)           │
│    avec features incluant  │
│    vol GARCH               │
└────────────────────────────┘
        ↓
┌────────────────────────────┐
│  Mesures de risque         │
│  - VaR / CVaR              │
│  - Volatilité prédite      │
└────────────────────────────┘
        ↓
┌────────────────────────────┐
│ Corrélations dynamiques    │
│ & Stress Testing           │
│ - Corrélations entre actifs│
│ - Scénarios de marché      │
└────────────────────────────┘
        ↓
Dashboard & Reporting

```



