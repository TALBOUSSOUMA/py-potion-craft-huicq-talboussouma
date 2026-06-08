import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# nettoyage.py
# Rôle : détecter et corriger les anomalies AUTOMATIQUEMENT
#        sur toutes les feuilles, sans coder les noms en dur
# ─────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).resolve().parent.parent
FILE       = BASE_DIR / "data" / "potions-craft.xlsx"
OUTPUT_DIR = BASE_DIR / "data"
excel      = pd.ExcelFile(FILE)

# ── Chargement dynamique de toutes les feuilles ───────────────
sheets = {
    feuille: pd.read_excel(excel, sheet_name=feuille)
    for feuille in excel.sheet_names
}

sheets_clean = {}

for nom, df in sheets.items():
    print(f"\n{'='*55}")
    print(f"  NETTOYAGE : {nom}")
    print(f"{'='*55}")
    df = df.copy()

    # ── 1. Corriger les espaces parasites dans les noms de colonnes
    cols_avant = df.columns.tolist()
    df.columns = df.columns.str.strip()
    cols_apres = df.columns.tolist()
    modifiees = [a for a, b in zip(cols_avant, cols_apres) if a != b]
    if modifiees:
        print(f"  ✔ Colonnes corrigées (espaces) : {modifiees}")

    # ── 2. Standardiser les noms de colonnes (tirets → underscores)
    df.columns = df.columns.str.replace("-", "_", regex=False)

    # ── 3. Trim des valeurs texte dans toutes les colonnes string
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # ── 4. Détecter et afficher les valeurs manquantes
    nan_counts = df.isnull().sum()
    nan_counts = nan_counts[nan_counts > 0]
    if len(nan_counts):
        print(f"  ⚠ Valeurs manquantes détectées :")
        for col, n in nan_counts.items():
            pct = round(n / len(df) * 100, 1)
            print(f"    • {col} : {n} NaN ({pct}%)")

            # Remplissage intelligent selon le type
            if df[col].dtype == "object":
                df[col] = df[col].fillna("Inconnu")
                print(f"      → Remplacé par 'Inconnu'")
            elif df[col].dtype in ["float64", "int64"]:
                mediane = df[col].median()
                df[col] = df[col].fillna(mediane)
                print(f"      → Remplacé par la médiane ({mediane})")
    else:
        print("  ✔ Aucune valeur manquante")

    # ── 5. Détecter les doublons
    nb_doublons = df.duplicated().sum()
    if nb_doublons:
        print(f"  ⚠ {nb_doublons} doublons supprimés")
        df = df.drop_duplicates()
    else:
        print("  ✔ Aucun doublon")

    # ── 6. Détecter les valeurs numériques aberrantes (prix, quantités)
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        negatifs = (df[col] < 0).sum()
        if negatifs:
            print(f"  ⚠ Colonne '{col}' : {negatifs} valeur(s) négative(s)")

    print(f"  → {len(df)} lignes conservées")
    sheets_clean[nom] = df

# ── Export : 1 CSV par feuille avec nom normalisé ─────────────
print("\n=== Export des feuilles nettoyées ===")
for nom, df in sheets_clean.items():
    nom_fichier = nom.replace("-", "_") + "_clean.csv"
    df.to_csv(OUTPUT_DIR / nom_fichier, index=False)
    print(f"  ✔ {nom_fichier} ({len(df)} lignes)")

print("\n✅ Nettoyage terminé")