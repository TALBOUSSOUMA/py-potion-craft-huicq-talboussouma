import pandas as pd
from pathlib import Path
from itertools import combinations
from collections import defaultdict
import re

# ─────────────────────────────────────────────────────────────
# transformation.py
# Rôle : restructurer et enrichir les données nettoyées
# ─────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FILE     = DATA_DIR / "potions-craft.xlsx"
xl       = pd.ExcelFile(FILE)

# ─────────────────────────────────────────────────────────────
# Détection automatique des feuilles
# ─────────────────────────────────────────────────────────────

def find_sheet(keyword):
    for sheet in xl.sheet_names:
        if keyword.lower() in sheet.lower():
            return sheet
    raise ValueError(f"Feuille contenant '{keyword}' introuvable")

sheet_potions = find_sheet("potions")
sheet_pi      = find_sheet("potions-inventeurs")
sheet_ingr    = find_sheet("ingredients")
sheet_types   = find_sheet("types-de-magie")
sheet_inv     = find_sheet("liste-inventeurs")

print("\nFeuilles détectées automatiquement :")
print("Potions      :", sheet_potions)
print("Inventeurs   :", sheet_pi)
print("Ingrédients  :", sheet_ingr)
print("Types magie  :", sheet_types)
print("Liste inv.   :", sheet_inv)

# Chargement dynamique
potions = pd.read_excel(xl, sheet_name=sheet_potions)
potions.columns = potions.columns.str.strip().str.replace("-", "_")
potions = potions.rename(columns={"quantite_ 2": "quantite_2"})

pi = pd.read_excel(xl, sheet_name=sheet_pi)
pi.columns = pi.columns.str.strip().str.replace("-", "_")
pi["inventeur"] = pi["inventeur"].fillna("Inconnu")

if "type_magie_potion" in pi.columns:
    pi = pi.rename(columns={"type_magie_potion": "type_magie"})

ingr = pd.read_excel(xl, sheet_name=sheet_ingr)
ingr.columns = ingr.columns.str.strip()

types = pd.read_excel(xl, sheet_name=sheet_types)
types.columns = types.columns.str.strip().str.replace("-", "_")

inv = pd.read_excel(xl, sheet_name=sheet_inv)
inv.columns = inv.columns.str.strip().str.replace("-", "_")

# ══════════════════════════════════════════════════════════════
# 1. FORMAT LONG : ingrédients par potion (wide → long)
# ══════════════════════════════════════════════════════════════
print("\n[1/4] Pivot ingrédients : wide → long")

slots = sorted(set(
    re.search(r"_(\d+)$", col).group(1)
    for col in potions.columns
    if re.search(r"ingredient_(\d+)$", col)
))
print(f"  Slots détectés : {slots}")

rows = []
for _, row in potions.iterrows():
    for i in slots:
        v = row.get(f"ingredient_{i}")
        if pd.notna(v) and str(v).strip():
            rows.append({
                "potion":      row["potion"],
                "ingredient":  v,
                "quantite":    row.get(f"quantite_{i}"),
                "unite":       row.get(f"unite_{i}"),
                "temperature": row.get(f"temperature_{i}"),
            })

recettes = pd.DataFrame(rows)
recettes.to_csv(DATA_DIR / "recettes.csv", index=False)
print(f"  ✔ recettes.csv — {len(recettes)} lignes")

# ══════════════════════════════════════════════════════════════
# 2. TABLE ANALYTIQUE : potions_final avec coût & bénéfice
# ══════════════════════════════════════════════════════════════
print("\n[2/4] Calcul du coût et du bénéfice")

unit_to_once = {
    "Pincée":  1 / 210,
    "Soufle":  7 / 210,
    "Nuage":   35 / 210,
    "Poignée": 105 / 210,
    "Once":    1,
}

ingr_prix  = ingr.set_index("ingredients")["prix"].to_dict()
type_comp  = types.set_index("type_de_magie")["competences"].to_dict()

def calcul_cout(potion_name):
    recette = recettes[recettes["potion"] == potion_name]
    cout = 0.0
    for _, r in recette.iterrows():
        prix_ingr = ingr_prix.get(r["ingredient"], 0)
        coeff = unit_to_once.get(r["unite"], 0)
        cout += r["quantite"] * coeff * prix_ingr
    return round(cout, 2)


# Fusion
potions_final = potions[["potion", "diluant", "prix"]].merge(
    pi[["potion", "type_magie", "inventeur"]], on="potion", how="left"
)
potions_final["cout"]        = potions_final["potion"].apply(calcul_cout)
potions_final["benefice"]    = (potions_final["prix"] - potions_final["cout"]).round(2)

# Compétences depuis types de magie
potions_final["competences"] = potions_final["type_magie"].map(type_comp)

# Nombre de potions par inventeur
nb_inv = potions_final.groupby("inventeur")["potion"].count().rename("nb_potions_inv")
potions_final = potions_final.merge(nb_inv, on="inventeur", how="left")

potions_final.to_csv(DATA_DIR / "potions_final.csv", index=False)
print(f"  ✔ potions_final.csv — {len(potions_final)} lignes")
print(f"  Colonnes : {potions_final.columns.tolist()}")
print(f"  competences NaN : {potions_final['competences'].isna().sum()}")

# ══════════════════════════════════════════════════════════════
# 3. EXPLOSION DES COMPÉTENCES
# ══════════════════════════════════════════════════════════════
print("\n[3/4] Explosion des compétences")

potions_comp = potions_final.copy()
potions_comp["competence"] = potions_comp["competences"].str.split(";")
potions_comp = potions_comp.explode("competence")
potions_comp["competence"] = potions_comp["competence"].str.strip()
potions_comp.to_csv(DATA_DIR / "potions_competences.csv", index=False)
print(f"  ✔ potions_competences.csv — {len(potions_comp)} lignes")

# ══════════════════════════════════════════════════════════════
# 4. MATRICE DE COOCCURRENCE DES INGRÉDIENTS
# ══════════════════════════════════════════════════════════════
print("\n[4/4] Matrice de cooccurrence")

potion_ingr_map = recettes.groupby("potion")["ingredient"].apply(list).to_dict()
cooc = defaultdict(int)
for ingrs in potion_ingr_map.values():
    for a, b in combinations(sorted(ingrs), 2):
        cooc[(a, b)] += 1
        cooc[(b, a)] += 1

freq      = recettes["ingredient"].value_counts()
top_ingrs = freq.head(20).index.tolist()
matrix    = [
    [cooc.get((a, b), 0) if a != b else int(freq[a]) for b in top_ingrs]
    for a in top_ingrs
]
cooc_df = pd.DataFrame(matrix, index=top_ingrs, columns=top_ingrs)
cooc_df.to_csv(DATA_DIR / "cooccurrences.csv")
print(f"  ✔ cooccurrences.csv — {len(top_ingrs)}×{len(top_ingrs)}")

# ══════════════════════════════════════════════════════════════
# 5. EXPORT INVENTEURS pour le graphe réseau
# ══════════════════════════════════════════════════════════════
print("\n[5/5] Export inventeurs")

# Construire le nom complet comme dans potions_final
inv["inventeur"] = inv["pseudo"].str.strip() + " " + inv["lignee"].str.strip()

# Compter les potions par inventeur (depuis potions_final)
nb_potions = potions_final.groupby("inventeur")["potion"].count().rename("nb_potions")

# Fusionner
inv_clean = inv.merge(nb_potions, on="inventeur", how="left")
inv_clean["nb_potions"] = inv_clean["nb_potions"].fillna(0).astype(int)

# Garder les colonnes utiles
inv_clean = inv_clean[["inventeur", "lignee", "nb_potions"]]

inv_clean.to_csv(DATA_DIR / "liste_inventeurs_clean.csv", index=False)
print(f"  ✔ liste_inventeurs_clean.csv — {len(inv_clean)} lignes")

print("\n✅ Transformation terminée")