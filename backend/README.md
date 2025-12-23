# FastAPI Backend - Structure du Projet

## 📁 Organisation

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Schémas Pydantic pour les réponses
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── masi.py             # Endpoints MASI
│   │   ├── opcvm.py            # Endpoints OPCVM Attijari
│   │   └── volatility.py       # Endpoints Volatilité
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration et chemins
│   │   └── data_loader.py      # Chargement et traitement des données CSV
│   └── __init__.py
├── main.py                      # Application FastAPI principale
├── requirements.txt             # Dépendances Python
└── README.md                    # Cette documentation
```

## 🚀 Démarrage Rapide

### 1. Installation des dépendances
```bash
cd backend
pip install -r requirements.txt
```

### 2. Lancer le serveur
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Accéder à l'API
- **Documentation interactive**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## 📊 Endpoints Disponibles

### MASI
- `GET /api/masi/data?period=6M` - Données MASI pour une période
- `GET /api/masi/latest` - Dernière valeur MASI
- `GET /api/masi/stats?period=6M` - Statistiques MASI

### OPCVM Attijari
- `GET /api/opcvm/data?period=6M` - Données OPCVM pour une période
- `GET /api/opcvm/latest` - Dernière valeur OPCVM
- `GET /api/opcvm/stats?period=6M` - Statistiques OPCVM

### Volatilité
- `GET /api/volatility/data?period=6M` - Données de volatilité
- `GET /api/volatility/forecast` - Prévision de volatilité (2 semaines)
- `GET /api/volatility/dashboard-stats?period=6M` - Statistiques du tableau de bord

## 🔧 Configuration

### Périodes Disponibles
- `1M` - 1 Mois (30 jours)
- `3M` - 3 Mois (90 jours)
- `6M` - 6 Mois (180 jours)
- `1Y` - 1 An (365 jours)
- `2Y` - 2 Ans (730 jours)

### CORS
L'API accepte les requêtes depuis:
- `http://localhost:3000` (Frontend React)
- `http://localhost:8000` (Tests locaux)

## 📝 Fichiers de Données

L'API utilise les fichiers CSV suivants:
- `../dataset_building/MASI_cleaned.csv` - Données MASI
- `../dataset_building/attijari_diversifie.csv` - Données OPCVM
- `../dataset_building/volatility_forecasted_dataset.csv` - Données de volatilité
- `../dataset_building/final_dataset.csv` - Dataset complet

## 🔌 Intégration Frontend

### Exemple avec React/TypeScript

```typescript
// Récupérer les données MASI
const response = await fetch('http://localhost:8000/api/masi/data?period=6M');
const masiData = await response.json();

// Récupérer les statistiques du tableau de bord
const statsResponse = await fetch('http://localhost:8000/api/volatility/dashboard-stats?period=6M');
const dashboardStats = await statsResponse.json();
```

## 📦 Schémas de Réponse

### MASIDataPoint
```json
{
  "date": "2024-12-22T10:30:00",
  "value": 13500.5,
  "variation": 2.15
}
```

### OPCVMDataPoint
```json
{
  "date": "2024-12-22T10:30:00",
  "value": 10250.75,
  "performance_1w": 1.5,
  "performance_1m": 3.2,
  "performance_6m": 8.5,
  "performance_1y": 12.3
}
```

### DashboardStats
```json
{
  "current_masi": 13500.5,
  "current_opcvm": 10250.75,
  "masi_change_percent": 2.15,
  "opcvm_change_percent": 3.5,
  "period": "6M",
  "last_update": "2024-12-22T10:30:00"
}
```

## 🛠️ Développement

### Ajouter un nouvel endpoint

1. Créer une fonction dans `app/routes/`
2. Utiliser le router FastAPI
3. Ajouter le schéma Pydantic dans `app/models/schemas.py`
4. Inclure la route dans `main.py`

### Modifier les sources de données

Éditer les chemins dans `app/utils/config.py` pour pointer vers d'autres fichiers CSV.

## 🚨 Gestion des Erreurs

- L'API retourne une réponse avec erreur si un fichier CSV est manquant
- Les données manquantes sont gérées gracieusement
- Les périodes invalides retournent une erreur descriptive
