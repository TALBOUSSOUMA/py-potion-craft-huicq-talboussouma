import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# analyse.py
# Rôle : statistiques descriptives AUTOMATIQUES sur toutes
#        les tables transformées, sans coder les noms en dur
# ─────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ── Chargement dynamique de tous les CSV finaux ───────────────
csv_files = list(DATA_DIR.glob("*.csv"))
tables = {}
for f in csv_files:
    if f.stat().st_size == 0:
        print(f"  ⚠ Ignoré (vide) : {f.name}")
        continue
    try:
        tables[f.stem] = pd.read_csv(f)
        print(f"  Chargé : {f.name}")
    except Exception as e:
        print(f"  ⚠ Erreur sur {f.name} : {e}")

print(f"\n  Tables disponibles : {list(tables.keys())}\n")

# ── Fonction utilitaire : rapport automatique sur n'importe quelle table
def rapport_table(nom, df):
    print(f"\n{'='*55}")
    print(f"  RAPPORT : {nom}")
    print(f"{'='*55}")
    print(f"  Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")

    # Stats sur colonnes numériques
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols):
        print(f"\n  Stats numériques :")
        print(df[num_cols].describe().round(2).to_string())

    # Stats sur colonnes catégorielles
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        n_unique = df[col].nunique()
        if 1 < n_unique <= 15:   # seulement si nombre de valeurs raisonnable
            print(f"\n  Distribution '{col}' ({n_unique} valeurs uniques) :")
            print(df[col].value_counts().to_string())

# ── Rapport générique sur toutes les tables ───────────────────
for nom, df in tables.items():
    rapport_table(nom, df)

# ══════════════════════════════════════════════════════════════
# ANALYSES MÉTIER : uniquement si potions_final existe
# ══════════════════════════════════════════════════════════════
if "potions_final" in tables:
    df = tables["potions_final"]
    print(f"\n{'='*55}")
    print("  ANALYSES MÉTIER — potions_final")
    print(f"{'='*55}")

    print(f"\n  Potions        : {len(df)}")
    print(f"  Inventeurs     : {df['inventeur'].nunique()}")
    print(f"  Types de magie : {df['type_magie'].nunique()}")

    print("\n  Top 5 potions les plus rentables :")
    print(df.nlargest(5, "benefice")[["potion", "type_magie", "inventeur", "benefice"]].to_string(index=False))

    print("\n  Bénéfice moyen par type de magie :")
    print(df.groupby("type_magie")["benefice"].agg(["mean", "min", "max"]).round(2).to_string())

    print("\n  Potions par inventeur :")
    print(df.groupby("inventeur")["potion"].count().sort_values(ascending=False).to_string())

    print("\n  Potions avec bénéfice négatif (perte) :")
    pertes = df[df["benefice"] < 0][["potion", "benefice"]]
    print(pertes.to_string(index=False) if len(pertes) else "  Aucune")

if "recettes" in tables:
    df_r = tables["recettes"]
    print(f"\n{'='*55}")
    print("  ANALYSES MÉTIER — recettes")
    print(f"{'='*55}")
    print(f"\n  Ingrédients distincts : {df_r['ingredient'].nunique()}")
    print(f"\n  Top 10 ingrédients les plus utilisés :")
    print(df_r["ingredient"].value_counts().head(10).to_string())
    print(f"\n  Nombre moyen d'ingrédients par potion : {df_r.groupby('potion')['ingredient'].count().mean():.1f}")

print("\n✅ Analyse terminée")