# Guide de Déploiement — Tableau de Bord Financier

Déploiement facile sur Vercel (Frontend) + Render (Backend) avec URL publique.

---

## **1. Préparer le projet**

### Frontend (React + Next.js)
```bash
cd react-financial-app

# Créer le fichier .env.local pour le développement local
cp .env.local.example .env.local

# Pour la production, tu défiras NEXT_PUBLIC_API_URL dans Vercel
```

### Backend (FastAPI)
```bash
cd backend

# Créer le fichier .env (optionnel, pour les vars d'env locales)
# Les vars de production seront définies dans Render
```

---

## **2. Déployer le Backend sur Render**

### Étapes:
1. **Créer un compte** sur [https://render.com](https://render.com)
2. **Connecter ton GitHub** (auto-sync)
3. **New → Web Service**
4. Sélectionner ton repo
5. **Configurer comme suit:**
   - **Name:** `financial-backend` (ou le nom que tu veux)
   - **Root Directory:** `backend`
   - **Runtime:** Python 3.11+
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 8000`

6. **Environment Variables (ajouter si nécessaire):**
   ```
   PYTHONUNBUFFERED=1
   ```

7. **Deploy!** → Attendre ~2-3 min

**Résultat:** Une URL comme `https://financial-backend-xxxxx.onrender.com`

---

## **3. Déployer le Frontend sur Vercel**

### Étapes:
1. **Créer un compte** sur [https://vercel.com](https://vercel.com)
2. **Importer le projet GitHub**
   - Ou via CLI: `npm i -g vercel && vercel`
3. **Configurer le déploiement:**
   - **Root Directory:** `react-financial-app`
   - **Framework Preset:** Next.js
   - Vercel détecte automatiquement

4. **Environment Variables (IMPORTANT):**
   - Dans la config Vercel, ajouter:
     ```
     NEXT_PUBLIC_API_URL = https://financial-backend-xxxxx.onrender.com
     ```
   - (Remplacer `xxxxx` par le vrai domaine Render)

5. **Deploy!** → Attendre ~1-2 min

**Résultat:** Une URL comme `https://financial-dashboard-xxxxx.vercel.app`

---

## **4. Vérifier que ça marche**

- Accéder à: `https://financial-dashboard-xxxxx.vercel.app`
- Les charts doivent charger les données depuis le backend
- Le bouton "Prédire la volatilité..." doit fonctionner

---

## **5. Alternative : Railway (Backend)**

Si Render ne te plaît pas, Railway est tout aussi simple:

1. Aller sur [https://railway.app](https://railway.app)
2. **New Project → Deploy from GitHub**
3. Sélectionner le repo et le branch
4. Railway détecte automatiquement Python + requirements.txt
5. Ajouter les vars d'env si nécessaire
6. Deploy en 1 clic!

**URL Backend:** `https://xxx-railway.up.railway.app`

---

## **6. Configuration CORS (si erreur)**

Si tu as une erreur CORS lors des appels API, modifier `backend/app/utils/config.py`:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://your-frontend.vercel.app",  # Ajouter ton URL Vercel
    "https://your-backend.onrender.com",  # Ajouter ton URL Render
]
```

---

## **7. Considérations importantes**

- **Données CSV**: Les fichiers `final_dataset.csv` et `volatility_forecasted_dataset.csv` doivent être dans `dataset_building/`
- **Temps de démarrage Render**: La première requête peut être lente (cold start ~10-15s). Considère un plan payant pour éviter.
- **Modelling.py**: S'exécute à chaque clic "Prédire". Sur un serveur sans GPU, cela peut prendre 30-60s.
- **Variables d'env**: Utilise `NEXT_PUBLIC_` au frontend pour que le navigateur puisse les lire.

---

## **8. Dépannage**

**Erreur CORS?**
→ Vérifier que `NEXT_PUBLIC_API_URL` est correct et que le backend accepte cet origin.

**404 sur les API?**
→ Vérifier que les fichiers CSV existent dans `dataset_building/`.

**Modelling.py timeout?**
→ Augmenter le délai timeout dans `backend/app/routes/volatility.py` ou optimiser le script.

---

## **Commandes locales (développement)**

```bash
# Frontend
cd react-financial-app
npm run dev  # http://localhost:3000

# Backend (dans une autre console)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Puis définir `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

Bon déploiement! 🚀
