# 🧪 Potion Craft — Dashboard Analytique

> Tableau de bord interactif pour archivistes magiques, construit avec Python & Streamlit.

---

## 🧙 Présentation

Ce projet transforme un fichier Excel désorganisé — contenant des potions, des ingrédients, des inventeurs et des types de magie — en un dashboard analytique entièrement interactif.

### Fonctionnalités

- 📊 **Top 10 des potions les plus rentables** — histogramme horizontal filtrable
- 🌀 **Hiérarchie magique** — diagramme sunburst (type de magie → compétence → potion)
- 🕸️ **Comparaison des compétences** — diagramme radar par potion
- 🔥 **Cooccurrences d'ingrédients** — heatmap des ingrédients qui apparaissent souvent ensemble
- 🔗 **Réseau d'inventeurs** — graphe interactif (couleur = lignée, taille = nombre de potions)

Tous les graphiques sont filtrables par **type de magie** ou par **inventeur** via la barre latérale.

---

## 🚀 Lancement rapide

### Prérequis

- Python 3.9 ou supérieur

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-compte/py-potion-craft-nom1-nom2.git
cd py-potion-craft-nom1-nom2

# 2. Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Exécution

```bash
# 4. Générer les fichiers CSV (pipeline de transformation)
python transformation.py

# 5. Lancer le dashboard
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur.

---

## 📁 Structure du projet

```
py-potion-craft-nom1-nom2/
├── data/
│   ├── potions-craft.xlsx          # Fichier source (Excel brut)
│   ├── recettes.csv                # Format long : une ligne par (potion, ingrédient)
│   ├── potions_final.csv           # Table analytique principale
│   ├── cooccurrences.csv           # Matrice de cooccurrence des ingrédients
│   ├── liste_inventeurs_clean.csv  # Données nettoyées pour le graphe réseau
│   ├── potions_competences.csv     # Compétences explosées (une ligne par compétence)
│   └── *_clean.csv                 # Fichiers intermédiaires (nettoyage)
├── scripts/
│   ├── extraction.py               # Exploration automatique des feuilles Excel
│   ├── nettoyage.py                # Nettoyage générique des données
│   ├── transformation.py           # Restructuration, conversions et calculs métier
│   └── analyse.py                  # Statistiques descriptives (optionnel)
├── app.py                          # Dashboard Streamlit
├── requirements.txt                # Dépendances Python
└── README.md
```

---

## 🛠️ Architecture technique

| Composant | Technologie | Justification |
|---|---|---|
| Exploration & nettoyage | Pandas | Lecture multi-feuilles, gestion des valeurs manquantes, transformations tabulaires |
| Conversion des unités | Dictionnaire Python | Facteurs déduits de la feuille `unites` (1 Once = 210 Pincées) |
| Calcul des coûts | Pandas + boucle | Quantité × facteur de conversion × prix unitaire à l'once |
| Visualisations | Plotly Express & Graph Objects | Graphiques interactifs (zoom, survol, légendes), intégration native Streamlit |
| Graphe de réseau | NetworkX + Plotly | NetworkX construit le graphe, Plotly gère le rendu interactif |
| Dashboard | Streamlit | Transformation d'un script Python en application web sans HTML/CSS |
| Versionning | Git & GitHub | Travail en équipe, traçabilité |

---

## 🔧 Pipeline de traitement

### 1. Extraction (`scripts/extraction.py`)

Parcourt toutes les feuilles du fichier Excel et produit un rapport automatique : dimensions, colonnes, types de données, valeurs manquantes. Permet de comprendre la structure sans rien coder en dur.

### 2. Nettoyage (`scripts/nettoyage.py`)

- Normalisation des noms de colonnes (suppression des espaces, remplacement des tirets par des underscores)
- Remplacement des valeurs manquantes (`"Inconnu"` pour les chaînes, médiane pour les numériques)
- Suppression des doublons
- Export de chaque feuille nettoyée en CSV

### 3. Transformation (`scripts/transformation.py`)

- **Détection des feuilles par mot-clé** via `find_sheet()` — aucun nom codé en dur
- **Format long** : une ligne par `(potion, ingrédient)` → `recettes.csv`
- **Conversion des unités** vers l'once :

  ```
  1 Once = 210 Pincées = 30 Soufles = 6 Nuages = 2 Brumes
  ```

  ```python
  unit_to_once = {
      "Pincée": 1/210,
      "Soufle": 7/210,
      "Nuage":  35/210,
      "Brume":  105/210,
      "Once":   1,
  }
  ```

- **Calcul du coût** : `quantité × conversion_once × prix_ingrédient`
- **Calcul du bénéfice** : `prix_vente − coût`
- **Explosion des compétences** : une potion peut avoir plusieurs compétences séparées par `;`
- **Matrice de cooccurrence** : pour chaque paire d'ingrédients, nombre de potions où ils apparaissent ensemble
- **Jointure** avec les inventeurs et les types de magie

### 4. Dashboard (`app.py`)

- Chargement des CSV finaux
- Filtres en barre latérale (type de magie, inventeur)
- 5 graphiques interactifs (voir [Fonctionnalités](#-présentation))
- Affichage des données brutes filtrées

---

## 🧩 Difficultés rencontrées

| Problème | Solution |
|---|---|
| Noms de feuilles variables selon les fichiers | Fonction `find_sheet()` avec recherche par mot-clé |
| Conversion des unités ambiguë | Analyse de la feuille `unites` pour déduire les facteurs ; prix catalogue considérés à l'once |
| Bénéfices négatifs inexpliqués | Correction de la conversion : division par 210 au lieu de multiplication ; vérification manuelle sur plusieurs potions |
| `KeyError: 'pseudo'` dans le graphe réseau | `liste_inventeurs_clean.csv` sans colonne `pseudo` → utilisation directe de la colonne `inventeur` |
| Matrice de cooccurrence illisible (trop d'ingrédients) | Limitation aux N ingrédients les plus fréquents, N étant réglable via un curseur interactif (défaut : 15) |

---

## 📦 Dépendances principales

```
pandas
openpyxl
streamlit
plotly
networkx
```

> Liste complète dans `requirements.txt`.