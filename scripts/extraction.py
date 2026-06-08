import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# extraction.py
# Rôle : explorer AUTOMATIQUEMENT toutes les feuilles
#        sans jamais coder en dur les noms des feuilles
#        → fonctionne même avec 100 feuilles et des milliers de lignes
# ─────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
FILE     = BASE_DIR / "data" / "potions-craft.xlsx"
excel    = pd.ExcelFile(FILE)

print(f"📂 Fichier : {FILE.name}")
print(f"📄 Nombre de feuilles : {len(excel.sheet_names)}")
print(f"📋 Feuilles : {excel.sheet_names}\n")

# ── Dictionnaire dynamique : on charge TOUT sans coder les noms ──
sheets = {}
for feuille in excel.sheet_names:
    sheets[feuille] = pd.read_excel(excel, sheet_name=feuille)

# ── Rapport automatique sur chaque feuille ───────────────────────
for nom, df in sheets.items():
    print("=" * 55)
    print(f"  FEUILLE : {nom}")
    print("=" * 55)
    print(f"  Dimensions     : {df.shape[0]} lignes × {df.shape[1]} colonnes")
    print(f"  Colonnes       : {df.columns.tolist()}")

    # Valeurs manquantes (seulement si il y en a)
    nan_counts = df.isnull().sum()
    nan_counts = nan_counts[nan_counts > 0]
    if len(nan_counts):
        print(f"  ⚠ Valeurs NaN  :\n{nan_counts.to_string()}")
    else:
        print("  ✔ Aucune valeur manquante")

    # Doublons
    nb_doublons = df.duplicated().sum()
    if nb_doublons:
        print(f"  ⚠ Doublons     : {nb_doublons} lignes")

    # Types de colonnes
    print(f"  Types de données :")
    for col, dtype in df.dtypes.items():
        exemple = df[col].dropna().iloc[0] if df[col].notna().any() else "vide"
        print(f"    • {col:<30} {str(dtype):<12} ex: {exemple}")

    print(f"  Aperçu :\n{df.head(2).to_string()}")
    print()

print("✅ Exploration terminée")
print(f"   → {len(sheets)} feuilles chargées dans le dictionnaire 'sheets'")
print(f"   → Accessible via : sheets['nom_de_la_feuille']")