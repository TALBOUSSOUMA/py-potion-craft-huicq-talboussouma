📜 Potion Craft
🧙‍♂️ Introduction (pour tout public)

Ce projet est un tableau de bord interactif destiné aux archivistes magiques. À partir d’un fichier Excel désorganisé contenant des potions, des ingrédients, des inventeurs et des types de magie, nous avons construit une application web qui permet de :

    Visualiser les 10 potions les plus rentables.

    Explorer la hiérarchie (type de magie → compétence → potion) avec un diagramme en anneau.

    Comparer les compétences des potions avec un diagramme radar.

    Détecter les ingrédients qui apparaissent souvent ensemble grâce à une heatmap.

    Voir les inventeurs et leurs potions sous forme de réseau (couleur = lignée, taille = nombre de potions).

L’application est entièrement interactive : on peut filtrer par type de magie ou par inventeur.
🛠️ Choix techniques (pour un expert)
Composant	Technologie	Justification
Exploration & nettoyage	Pandas	Lecture des feuilles Excel, gestion des valeurs manquantes, transformation des colonnes. Robuste et adapté à des données tabulaires désorganisées.
Conversion des unités	Dictionnaire Python	Déduit des relations 7 Pincée → 1 Soufle, 5 Soufle → 1 Nuage, etc. Pour obtenir un coût cohérent, nous sommes partis du principe que les prix dans liste-ingredients sont à l’once.
Calcul du coût	Pandas + boucle	Chaque potion voit ses ingrédients convertis en onces, multipliés par le prix unitaire, puis sommés.
Visualisations interactives	Plotly Express & Graph Objects	Intégration native avec Streamlit, graphiques dynamiques (zoom, survol, légendes).
Graphe de réseau	NetworkX + Plotly	NetworkX construit le graphe, Plotly le rend interactif. Couleurs et tailles de nœuds contrôlées.
Application web	Streamlit	Imposé par l’énoncé. Permet de transformer un script Python en dashboard sans connaissance HTML/CSS.
Gestion de version	Git & GitHub	Travail en équipe, traçabilité, dépôt privé.
🔧 Pipeline de traitement (étapes techniques)
1. Extraction automatique (extraction.py)

    Parcourt toutes les feuilles du fichier Excel.

    Affiche un rapport (dimensions, colonnes, valeurs manquantes, types).

    Permet de comprendre la structure sans rien coder en dur.

2. Nettoyage générique (nettoyage.py)

    Supprime les espaces dans les noms de colonnes.

    Remplace les tirets par des underscores.

    Remplit les valeurs manquantes :

        "Inconnu" pour les chaînes.

        Médiane pour les nombres.

    Supprime les lignes en double.

    Exporte chaque feuille nettoyée en CSV.

3. Transformation métier (transformation.py)

    Détection des feuilles par mot‑clé (find_sheet()) – pas de noms codés.

    Passage en format long : une ligne par (potion, ingrédient) → recettes.csv.

    Conversion des unités :

        Relation déduite : 1 Once = 210 Pincées.

        Dictionnaire unit_to_once :
        "Pincée": 1/210, "Soufle": 7/210, etc.

    Calcul du coût :
    coût = quantite × (conversion en onces) × prix_ingredient_à_l_once.

    Calcul du bénéfice :
    bénéfice = prix_vente - coût.

    Jointure avec les inventeurs et le type de magie.

    Explosion des compétences (une potion peut avoir plusieurs compétences via ;).

    Matrice de cooccurrence : pour chaque paire d’ingrédients, nombre de potions où ils apparaissent ensemble.

    Export final : potions_final.csv, cooccurrences.csv, liste_inventeurs_clean.csv, etc.

4. Dashboard Streamlit (app.py)

    Chargement des CSV finaux.

    Barre latérale avec deux filtres (type de magie, inventeur).

    5 graphiques :

        Histogramme horizontal (top 10 bénéfices).

        Sunburst (type → compétence → potion).

        Radar (nombre de potions par compétence).

        Heatmap de cooccurrence (choix du nombre d’ingrédients).

        Réseau (inventeurs – potions).

    Affichage des données brutes filtrées.

🧩 Difficultés rencontrées et solutions
Difficulté	Solution
Noms de feuilles variables	Fonction find_sheet() qui cherche un mot‑clé dans le nom de la feuille.
Conversion des unités ambiguë	Analyse de la feuille unites pour déduire les facteurs 1, 7, 35, 105, 210. Choix final de convertir en onces car les prix catalogue semblent être à l’once.
Bénéfices négatifs inexpliqués	Correction de la conversion : au lieu de multiplier par 210 (pincées), on divise par 210 (onces). Vérification sur quelques potions.
Graphe de réseau qui plante (KeyError: 'pseudo')	Adaptation du code : le fichier liste_inventeurs_clean.csv ne contient pas de colonne pseudo. On utilise directement inventeur.
Cooccurrence trop grande	On limite l’affichage aux 15 ingrédients les plus fréquents (curseur interactif).
🚀 Lancement du projet
Prérequis

    Python 3.9 ou supérieur

    Les bibliothèques listées dans requirements.txt

Installation
bash

# 1. Cloner le dépôt (ou décompresser l'archive)
git clone https://github.com/votre-compte/py-potion-craft-nom1-nom2.git
cd py-potion-craft-nom1-nom2

# 2. (Optionnel) Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # sur Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

Exécution
bash

# 4. Lancer le pipeline de transformation (génère les CSV)
python transformation.py

# 5. Lancer l'application Streamlit
streamlit run app.py

L’application s’ouvre automatiquement dans ton navigateur.
📁 Structure du projet

py-potion-craft-huicq-talboussouma/
├── data/
│   ├── potions-craft.xlsx                # Fichier source (Excel)
│   ├── recettes.csv                      # Généré par transformation.py
│   ├── potions_final.csv                 # Généré par transformation.py (table analytique)
│   ├── cooccurrences.csv                 # Généré par transformation.py (matrice)
│   ├── liste_inventeurs_clean.csv        # Généré par transformation.py (pour le graphe)
│   ├── potions_competences.csv           # Généré par transformation.py (explosion)
│   ├── *_clean.csv                       # Autres fichiers intermédiaires (nettoyage)
│   └── ...                               # (peuvent être ignorés pour l'application finale)
├── scripts/
│   ├── extraction.py                     # Exploration automatique des feuilles
│   ├── nettoyage.py                      # Nettoyage générique
│   ├── transformation.py                 # Restructuration et calculs métier
│   └── analyse.py                        # Statistiques descriptives (optionnel)
├── app.py                                # Dashboard Streamlit
├── requirements.txt                      # Dépendances Python
└── README.md                             # Ce document