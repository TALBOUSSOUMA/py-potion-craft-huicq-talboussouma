import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from itertools import combinations
from collections import defaultdict
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Potion Craft — Archives Magiques",
    page_icon="🧪",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MAGIC_COLORS = {
    "Bleue":   "#4A90D9",
    "Noire":   "#1a1a1a",
    "Blanche": "#D4C9A8",
    "Rouge":   "#C0392B",
    "Verte":   "#27AE60",
    "Pourpre": "#8E44AD",
    "Inconnu": "#95A5A6",
}

# ─────────────────────────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load():
    potions_final = pd.read_csv(DATA_DIR / "potions_final.csv")
    recettes      = pd.read_csv(DATA_DIR / "recettes.csv")
    inventeurs    = pd.read_csv(DATA_DIR / "liste_inventeurs_clean.csv")
    # Afficher les colonnes réelles pour debug
    return potions_final, recettes, inventeurs

potions_final, recettes, inventeurs = load()

# ─────────────────────────────────────────────────────────────
# Détection automatique du nom de la colonne type de magie
# ─────────────────────────────────────────────────────────────
col_type = next(
    (c for c in potions_final.columns if "magie" in c.lower()),
    None
)
if col_type is None:
    st.error(f"Colonne type de magie introuvable. Colonnes disponibles : {potions_final.columns.tolist()}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧪 Potion Craft")
    st.caption("Archives Magiques du Ministère")
    st.divider()

    types_dispo = ["Tous"] + sorted(potions_final[col_type].dropna().unique().tolist())
    filtre_type = st.selectbox("Type de magie", types_dispo)

    inventeurs_dispo = ["Tous"] + sorted([
        i for i in potions_final["inventeur"].unique()
        if isinstance(i, str) and i != "Inconnu"
    ])
    filtre_inv = st.selectbox("Inventeur", inventeurs_dispo)
    st.divider()
    st.caption("Atelier Reporting — Datavisualisation")

# Filtrage
df = potions_final.copy()
if filtre_type != "Tous":
    df = df[df[col_type] == filtre_type]
if filtre_inv != "Tous":
    df = df[df["inventeur"] == filtre_inv]

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
            padding:2rem 2.5rem;border-radius:14px;margin-bottom:1.5rem">
    <h1 style="color:#e2c97e;margin:0;font-size:2.2rem">
        📜 Archives Magiques du Ministère
    </h1>
    <p style="color:#aab8c2;margin:.4rem 0 0">
        Rapport interactif — Potions · Ingrédients · Inventeurs
    </p>
</div>
""", unsafe_allow_html=True)

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("🧪 Potions",        len(df))
c2.metric("💰 Prix moyen",     f"{df['prix'].mean():.0f} 🪙")
c3.metric("📈 Bénéfice moyen", f"{df['benefice'].mean():.0f} 🪙")
c4.metric("🔮 Types de magie", df[col_type].nunique())
st.divider()

# ═════════════════════════════════════════════════════════════
# VIZ 1 — Histogramme horizontal Top 10 potions rentables
# ═════════════════════════════════════════════════════════════
st.subheader("📊 Top 10 — Potions les plus rentables")
st.caption("Longueur de barre = bénéfice (pièces d'or) · Couleur = type de magie")

top10 = df.nlargest(10, "benefice").sort_values("benefice")
colors_bar = [MAGIC_COLORS.get(t, "#888") for t in top10[col_type]]

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=top10["benefice"],
    y=top10["potion"],
    orientation="h",
    marker=dict(color=colors_bar, line=dict(color="rgba(0,0,0,.15)", width=1)),
    text=[f"{v:.0f} 🪙" for v in top10["benefice"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Bénéfice : %{x:.0f} pièces d'or<extra></extra>",
))
for magic in top10[col_type].unique():
    fig1.add_trace(go.Bar(
        x=[None], y=[None], orientation="h",
        name=magic, marker_color=MAGIC_COLORS.get(magic, "#888"),
        showlegend=True,
    ))
fig1.update_layout(
    height=420, margin=dict(l=10, r=120, t=10, b=40),
    xaxis_title="Bénéfice (pièces d'or)",
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    legend_title="Type de magie",
    xaxis=dict(showgrid=True, gridcolor="#eee"),
)
st.plotly_chart(fig1, use_container_width=True)
st.divider()

# ═════════════════════════════════════════════════════════════
# VIZ 2 — Sunburst
# ═════════════════════════════════════════════════════════════
st.subheader("🌀 Sunburst — Répartition par type de magie & compétence")
st.caption("Catalogue → Type de magie → Compétence associée")

rows_sun = []

for _, row in potions_final.iterrows():

    if pd.notna(row["competences"]):

        for comp in str(row["competences"]).split(";"):

            rows_sun.append({
                "Type de magie": row[col_type],
                "Compétence": comp.strip(),
                "Potion": row["potion"]
            })

sun_df = pd.DataFrame(rows_sun)

fig2 = px.sunburst(
    sun_df,
    path=[
        "Type de magie",
        "Compétence",
        "Potion"
    ]
)

fig2.update_layout(
    height=650,
    margin=dict(t=20, l=20, r=20, b=20)
)

st.plotly_chart(fig2, use_container_width=True)
st.divider()

# ═════════════════════════════════════════════════════════════
# VIZ 3 — Kiviat
# ═════════════════════════════════════════════════════════════
st.subheader("🕸️ Kiviat — Nombre de potions par compétence")
st.caption("Chaque axe = une compétence · Longueur = nombre de potions")

# Utiliser potions_final complet pour le Kiviat (pas df filtré)
comp_list = []
for _, row in potions_final.iterrows():
    if pd.notna(row.get("competences")):
        for c in str(row["competences"]).split(";"):
            comp_list.append(c.strip())

if not comp_list:
    st.warning("Aucune compétence disponible.")
else:
    comp_counts = pd.Series(comp_list).value_counts().reset_index()
    comp_counts.columns = ["competence", "count"]
    comp_counts = comp_counts.sort_values("competence")

    cats   = comp_counts["competence"].tolist()
    vals   = comp_counts["count"].tolist()
    cats_c = cats + [cats[0]]
    vals_c = vals + [vals[0]]

    fig3 = go.Figure(go.Scatterpolar(
        r=vals_c, theta=cats_c,
        fill="toself",
        fillcolor="rgba(74,144,217,0.2)",
        line=dict(color="#4A90D9", width=2),
        marker=dict(size=7, color="#4A90D9"),
        hovertemplate="<b>%{theta}</b><br>Potions : %{r}<extra></extra>",
    ))
    fig3.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(vals) + 2]),
            angularaxis=dict(tickfont=dict(size=12)),
        ),
        height=460, paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=30, l=60, r=60),
    )
    st.plotly_chart(fig3, use_container_width=True)
st.divider()

# ═════════════════════════════════════════════════════════════
# VIZ 4 — Heatmap cooccurrence
# ═════════════════════════════════════════════════════════════
st.subheader("🌡️ Heatmap — Cooccurrence des ingrédients")
st.caption("Nombre de recettes où deux ingrédients apparaissent ensemble")

top_n = st.slider("Nombre d'ingrédients", min_value=8, max_value=25, value=15)

potion_ingr = recettes.groupby("potion")["ingredient"].apply(list).to_dict()
cooc = defaultdict(int)
for ingrs in potion_ingr.values():
    for a, b in combinations(sorted(ingrs), 2):
        cooc[(a, b)] += 1
        cooc[(b, a)] += 1

freq      = recettes["ingredient"].value_counts()
top_ingrs = freq.head(top_n).index.tolist()
short     = lambda s: s[:16] + "…" if len(s) > 16 else s
labels_hm = [short(i) for i in top_ingrs]

matrix = [
    [cooc.get((a, b), 0) if a != b else int(freq[a]) for b in top_ingrs]
    for a in top_ingrs
]

fig4 = go.Figure(go.Heatmap(
    z=matrix, x=labels_hm, y=labels_hm,
    colorscale="YlOrRd",
    hovertemplate="<b>%{y}</b> + <b>%{x}</b><br>Cooccurrences : %{z}<extra></extra>",
    text=[[str(v) if v > 0 else "" for v in row] for row in matrix],
    texttemplate="%{text}", textfont=dict(size=9),
))
fig4.update_layout(
    height=550,
    xaxis=dict(tickangle=-40, tickfont=dict(size=10)),
    yaxis=dict(tickfont=dict(size=10)),
    margin=dict(t=20, b=120, l=160, r=20),
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig4, use_container_width=True)
st.divider()

# ═════════════════════════════════════════════════════════════
# VIZ 5 — Graphe de réseau
# ═════════════════════════════════════════════════════════════
st.subheader("🔗 Réseau — Inventeurs & leurs potions")
st.caption("Couleur nœud inventeur = lignée · Taille = nombre de potions créées")

lignees  = inventeurs["lignee"].dropna().unique()
palette  = px.colors.qualitative.Set2
lig_cols = {l: palette[i % len(palette)] for i, l in enumerate(lignees)}

# La colonne 'inventeur' contient déjà le nom complet (ex: "Gandalf Rogue")
inv_map = inventeurs.set_index("inventeur")["lignee"].to_dict()

G = nx.Graph()
nb_par_inv = potions_final.groupby("inventeur")["potion"].count().to_dict()

for inv_name, lignee in inv_map.items():
    G.add_node(inv_name, ntype="inventeur", lignee=lignee, nb=nb_par_inv.get(inv_name, 0))

for _, row in potions_final.iterrows():
    if isinstance(row["inventeur"], str) and row["inventeur"] != "Inconnu":
        G.add_node(row["potion"], ntype="potion", type_magie=row[col_type])
        G.add_edge(row["inventeur"], row["potion"])

pos = nx.spring_layout(G, seed=42, k=2.2)

ex, ey = [], []
for u, v in G.edges():
    x0, y0 = pos[u]; x1, y1 = pos[v]
    ex += [x0, x1, None]; ey += [y0, y1, None]

edge_trace = go.Scatter(
    x=ex, y=ey, mode="lines",
    line=dict(width=0.7, color="#bbb"), hoverinfo="none",
)

nx_list, ny_list, ncolor, nsize, ntext, nhover = [], [], [], [], [], []
for node, data in G.nodes(data=True):
    x, y = pos[node]
    nx_list.append(x); ny_list.append(y)
    if data.get("ntype") == "inventeur":
        lig = data.get("lignee", "?")
        nb  = data.get("nb", 1)
        ncolor.append(lig_cols.get(lig, "#888"))
        nsize.append(20 + nb * 7)
        ntext.append(node)
        nhover.append(f"<b>{node}</b><br>Inventeur · Lignée : {lig}<br>Potions : {nb}")
    else:
        tm = data.get("type_magie", "?")
        ncolor.append(MAGIC_COLORS.get(tm, "#ccc"))
        nsize.append(10)
        ntext.append("")
        nhover.append(f"<b>{node}</b><br>Potion · Magie : {tm}")

node_trace = go.Scatter(
    x=nx_list, y=ny_list,
    mode="markers+text",
    text=ntext, textposition="top center",
    textfont=dict(size=9),
    marker=dict(size=nsize, color=ncolor,
                line=dict(width=1.5, color="white"), opacity=0.9),
    hovertext=nhover, hoverinfo="text",
)

fig5 = go.Figure(data=[edge_trace, node_trace])

for lig, col in lig_cols.items():
    fig5.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=12, color=col),
        name=f"Lignée {lig}", showlegend=True,
    ))

fig5.update_layout(
    height=580, hovermode="closest",
    showlegend=True, legend_title="Lignées",
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    margin=dict(t=20, b=20, l=20, r=20),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig5, use_container_width=True)
st.divider()

# ─────────────────────────────────────────────────────────────
# DONNÉES BRUTES
# ─────────────────────────────────────────────────────────────
with st.expander("📋 Données brutes — potions filtrées"):
    st.dataframe(df, use_container_width=True, height=320)

st.caption("📜 Archives Magiques du Ministère · Potion Craft · CC-BY-NC-ND")