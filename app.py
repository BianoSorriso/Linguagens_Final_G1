import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import json
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mercado Imobiliário · Analytics",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS – dark premium theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp {
      background: linear-gradient(135deg, #0c1512 0%, #10201b 50%, #0c1512 100%);
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #12201c 0%, #10201b 100%) !important;
      border-right: 1px solid rgba(94,234,212,0.15);
  }
  [data-testid="stSidebar"] * { color: #e6efe9 !important; }
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
      background: linear-gradient(135deg, #14b8a6, #2dd4bf) !important;
      border-radius: 6px !important;
  }

  /* Hero */
  .hero-section {
      background: linear-gradient(135deg, #1b2b26 0%, #0f1b17 100%);
      border: 1px solid rgba(94,234,212,0.2);
      border-radius: 16px;
      padding: 2rem 2.5rem;
      margin-bottom: 1.5rem;
      position: relative;
      overflow: hidden;
  }
  .hero-section::before {
      content: '';
      position: absolute;
      top: -50%; right: -20%;
      width: 400px; height: 400px;
      background: radial-gradient(circle, rgba(20,184,166,0.08) 0%, transparent 70%);
      border-radius: 50%;
  }
  .hero-title {
      font-size: 2rem; font-weight: 700;
      background: linear-gradient(135deg, #5eead4, #2dd4bf, #e9c46a);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0 0 0.5rem 0;
  }
  .hero-subtitle {
      color: #a3b8ad; font-size: 0.95rem; line-height: 1.6; margin: 0;
  }
  .hero-badge {
      display: inline-block;
      background: linear-gradient(135deg, #14b8a6, #2dd4bf);
      color: white; font-size: 0.7rem; font-weight: 600;
      padding: 3px 10px; border-radius: 20px;
      margin-bottom: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase;
  }

  /* KPI Cards */
  .kpi-card {
      background: linear-gradient(135deg, #1b2b26 0%, #15241f 100%);
      border: 1px solid rgba(94,234,212,0.15);
      border-radius: 14px; padding: 1.1rem 1rem;
      text-align: center; position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
      height: 100%;
  }
  .kpi-card:hover { transform: translateY(-3px); border-color: rgba(94,234,212,0.4); }
  .kpi-card::after {
      content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
      background: linear-gradient(90deg, #14b8a6, #2dd4bf);
  }
  .kpi-icon   { font-size: 1.5rem; margin-bottom: 0.3rem; display: block; }
  .kpi-label  { color: #7d9488; font-size: 0.68rem; font-weight: 600;
                text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
  .kpi-value  { color: #e6efe9; font-size: 1.15rem; font-weight: 700; line-height: 1.2; }
  .kpi-value.accent { color: #5eead4; }
  .kpi-value.green  { color: #34d399; }

  /* Section headers */
  .section-header {
      display: flex; align-items: center; gap: 0.6rem;
      margin-bottom: 1.2rem; padding-bottom: 0.75rem;
      border-bottom: 1px solid rgba(94,234,212,0.1);
  }
  .section-header h3 { color: #e6efe9; font-size: 1.1rem; font-weight: 600; margin: 0; }
  .section-dot {
      width: 8px; height: 8px;
      background: linear-gradient(135deg, #14b8a6, #2dd4bf); border-radius: 50%;
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
      background: #12201c; border-radius: 12px; padding: 4px; gap: 4px;
      border: 1px solid rgba(94,234,212,0.1);
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
      background: transparent; color: #7d9488 !important;
      border-radius: 8px; font-size: 0.82rem; font-weight: 500;
      padding: 8px 16px; transition: all 0.2s;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
      background: linear-gradient(135deg, #14b8a6, #0f766e) !important;
      color: #fff !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

  /* Misc */
  [data-testid="stDataFrame"] {
      border: 1px solid rgba(94,234,212,0.1) !important;
      border-radius: 12px !important; overflow: hidden;
  }
  [data-testid="stAlert"] { border-radius: 12px !important; border-width: 1px !important; }
  hr { border-color: rgba(94,234,212,0.1) !important; }

  .sidebar-brand {
      display: flex; align-items: center; gap: 0.5rem;
      padding: 1rem 0 1.5rem 0;
      border-bottom: 1px solid rgba(94,234,212,0.1); margin-bottom: 1.2rem;
  }
  .sidebar-brand-text { font-size: 1rem; font-weight: 700; color: #e6efe9; }
  .sidebar-brand-sub  { font-size: 0.72rem; color: #7d9488; }

  .insight-box {
      background: rgba(20,184,166,0.06);
      border: 1px solid rgba(20,184,166,0.2);
      border-left: 3px solid #14b8a6;
      border-radius: 10px; padding: 0.85rem 1.1rem;
      color: #a3b8ad; font-size: 0.88rem; line-height: 1.65;
      margin-top: 0.8rem;
  }
  .insight-box strong { color: #5eead4; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MATPLOTLIB DARK THEME
# ─────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#1b2b26",
    "axes.facecolor":    "#1b2b26",
    "axes.edgecolor":    "#34483f",
    "axes.labelcolor":   "#a3b8ad",
    "xtick.color":       "#7d9488",
    "ytick.color":       "#7d9488",
    "text.color":        "#e6efe9",
    "grid.color":        "#2a4a42",
    "grid.linewidth":    0.6,
    "axes.grid":         True,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "DejaVu Sans",
    "axes.titlecolor":   "#e6efe9",
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    10,
})

ACCENT  = "#14b8a6"
ACCENT2 = "#2dd4bf"
ACCENT3 = "#e9c46a"
GREEN   = "#34d399"
PALETTE_COOL = ["#2dd4bf","#e9c46a","#7fb7a4","#d4a373","#9ad1b3","#c7b299","#5aa9a0","#e6ccb2","#8fbc8f","#b5a642"]
PALETTE_BLUE = [ACCENT, ACCENT2, "#2dd4bf", "#6ee7b7", "#a7f3d0"]
PALETTE_PURP = ["#e9c46a","#d4a373","#c9a66b","#b08968","#9c7a54"]

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def section(title: str):
    st.markdown(f"""
    <div class="section-header">
      <div class="section-dot"></div>
      <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)

def descrever_corr(c: float) -> str:
    """Classifica a força de uma correlação para os textos interpretativos."""
    a = abs(c)
    if a < 0.1:  return "praticamente nula"
    if a < 0.3:  return "fraca"
    if a < 0.6:  return "moderada"
    return "forte"

def insight(text: str):
    st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PATHS & DATA
# ─────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
CAMINHO_DADOS = BASE_DIR / "dados" / "simulacao_mercado_imobiliario_brasil.csv"
CAMINHO_BANCO = BASE_DIR / "database" / "mercado_imobiliario.sqlite"
CAMINHO_BANCO.parent.mkdir(exist_ok=True)

@st.cache_data
def carregar_dados_csv():
    df = pd.read_csv(CAMINHO_DADOS)
    df["data"]    = pd.to_datetime(df["data"], errors="coerce")
    df["ano"]     = df["data"].dt.year
    df["mes"]     = df["data"].dt.month
    df["ano_mes"] = df["data"].dt.to_period("M").astype(str)
    return df

def criar_banco_sqlite(df):
    engine = create_engine(f"sqlite:///{CAMINHO_BANCO}")
    df.to_sql("imoveis", engine, if_exists="replace", index=False)
    return engine

df     = carregar_dados_csv()
engine = criar_banco_sqlite(df)

# ─────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <span class="hero-badge">🏙️ Analytics Platform · Brasil 2015–2024</span>
  <h1 class="hero-title">Mercado Imobiliário Brasileiro</h1>
  <p class="hero-subtitle">
    Análise profunda do comportamento imobiliário no Brasil entre 2015 e 2024 —
    evolução de preços, diferenças regionais, valorização e relação renda × imóveis.<br>
    <strong style="color:#5eead4">Pandas</strong> &nbsp;·&nbsp;
    <strong style="color:#2dd4bf">Seaborn / Matplotlib</strong> &nbsp;·&nbsp;
    <strong style="color:#5eead4">Plotly</strong> &nbsp;·&nbsp;
    <strong style="color:#e9c46a">SQLite + SQLAlchemy</strong> &nbsp;·&nbsp;
    <strong style="color:#34d399">NumPy</strong>
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""

    """, unsafe_allow_html=True)

    st.markdown("**Filtros de Análise**")

    regioes = sorted(df["regiao"].dropna().unique())
    ufs     = sorted(df["uf"].dropna().unique())
    tipos   = sorted(df["tipo_imovel"].dropna().unique())
    niveis  = sorted(df["nivel_preco"].dropna().unique())

    regiao_sel = st.multiselect("🗺️ Região",         options=regioes, default=regioes)
    uf_sel     = st.multiselect("📍 UF",              options=ufs,     default=ufs)
    tipo_sel   = st.multiselect("🏠 Tipo de Imóvel",  options=tipos,   default=tipos)
    nivel_sel  = st.multiselect("💰 Nível de Preço",  options=niveis,  default=niveis)

    st.markdown("---")
    data_min = df["data"].min().date()
    data_max = df["data"].max().date()
    intervalo_datas = st.date_input(
        "📅 Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )

if isinstance(intervalo_datas, tuple) and len(intervalo_datas) == 2:
    inicio, fim = intervalo_datas
else:
    inicio, fim = data_min, data_max

# ─────────────────────────────────────────────
#  FILTRO DINÂMICO
# ─────────────────────────────────────────────
df_filtrado = df[
    (df["regiao"].isin(regiao_sel))     &
    (df["uf"].isin(uf_sel))             &
    (df["tipo_imovel"].isin(tipo_sel))  &
    (df["nivel_preco"].isin(nivel_sel)) &
    (df["data"].dt.date >= inicio)      &
    (df["data"].dt.date <= fim)
]

if df_filtrado.empty:
    st.warning("⚠️  Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

# ─────────────────────────────────────────────
#  KPIs CALCULADOS
# ─────────────────────────────────────────────
preco_medio   = df_filtrado["preco_imovel"].mean()
m2_medio      = df_filtrado["preco_m2"].mean()
renda_media   = df_filtrado["renda_media"].mean()
juros_medio   = df_filtrado["taxa_juros"].mean()
total_imoveis = len(df_filtrado)

# Cidade mais cara
cidade_cara_row = (
    df_filtrado.groupby("cidade")["preco_imovel"].mean()
    .sort_values(ascending=False)
    .reset_index().iloc[0]
)
cidade_cara = cidade_cara_row["cidade"]

# Região mais cara
regiao_cara = (
    df_filtrado.groupby("regiao")["preco_imovel"].mean()
    .idxmax()
)

# Tipo mais valorizado
tipo_topo = (
    df_filtrado.groupby("tipo_imovel")["preco_imovel"].mean()
    .idxmax()
)

# Crescimento médio anual (CAGR preço médio)
preco_ano = (
    df_filtrado.groupby("ano")["preco_imovel"].mean()
    .sort_index()
)
if len(preco_ano) >= 2:
    anos_range = preco_ano.index[-1] - preco_ano.index[0]
    cagr = ((preco_ano.iloc[-1] / preco_ano.iloc[0]) ** (1 / max(anos_range, 1)) - 1) * 100
else:
    cagr = 0.0

# ─────────────────────────────────────────────
#  KPI CARDS — linha 1 (5 cards)
# ─────────────────────────────────────────────
kpi_row1 = [
    ("🏷️", "Preço Médio",          fmt_brl(preco_medio),                     ""),
    ("📐", "Preço / m²",            fmt_brl(m2_medio),                        ""),
    ("💵", "Renda Média Regional",  fmt_brl(renda_media),                     ""),
    ("📈", "Taxa de Juros",         f"{juros_medio:.2f}%",                    "accent"),
    ("🏘️", "Volume Analisado",     f"{total_imoveis:,.0f}".replace(",","."), "accent"),
]

cols = st.columns(5)
for col, (icon, label, value, cls) in zip(cols, kpi_row1):
    col.markdown(f"""
    <div class="kpi-card">
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value {cls}">{value}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# KPI linha 2 (4 cards adicionais exigidos)
kpi_row2 = [
    ("🏆", "Cidade Mais Cara",        cidade_cara,          "accent"),
    ("🗺️", "Região Mais Cara",        regiao_cara,          "accent"),
    ("🥇", "Tipo Mais Valorizado",     tipo_topo,            ""),
    ("📊", "Crescimento Médio Anual",  f"{cagr:.1f}% a.a.",  "green"),
]

cols2 = st.columns(4)
for col, (icon, label, value, cls) in zip(cols2, kpi_row2):
    col.markdown(f"""
    <div class="kpi-card">
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value {cls}">{value}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba_plotly, aba4, aba5, aba6 = st.tabs([
    "📈  Evolução Temporal",
    "🏠  Tipologia e Níveis",
    "🗺️  Análise Geográfica",
    "🌐  Mapas Interativos",
    "🔗  Correlações",
    "🗄️  Consulta SQL",
    "📋  Base de Dados",
])

# ══════════════════════════════════════════════
#  ABA 1 — EVOLUÇÃO TEMPORAL
# ══════════════════════════════════════════════
with aba1:
    # --- Gráfico 1: Linha temporal de preço médio mensal ---
    section("Evolução Mensal do Preço Médio dos Imóveis")

    serie_mensal = (
        df_filtrado.groupby("ano_mes")["preco_imovel"]
        .mean().reset_index().sort_values("ano_mes")
    )

    fig, ax = plt.subplots(figsize=(13, 4.5))
    fig.patch.set_facecolor("#1b2b26")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
    ax.fill_between(range(len(serie_mensal)), serie_mensal["preco_imovel"], alpha=0.12, color=ACCENT)
    ax.plot(range(len(serie_mensal)), serie_mensal["preco_imovel"],
            color=ACCENT, linewidth=2.2, marker="o", markersize=3.5,
            markerfacecolor=ACCENT2, markeredgecolor="#1b2b26", markeredgewidth=1.5)
    step = max(1, len(serie_mensal) // 12)
    ticks = list(range(0, len(serie_mensal), step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([serie_mensal["ano_mes"].iloc[i] for i in ticks], rotation=40, ha="right", fontsize=8)
    ax.set_title("Evolução Temporal de Preços — Visão Mensal", pad=14)
    ax.set_xlabel("Período (Ano-Mês)")
    ax.set_ylabel("Preço Médio (R$)")
    st.pyplot(fig, use_container_width=True)

    insight(
        f"📊 No período filtrado, o preço médio mensal oscila entre <strong>{fmt_brl(serie_mensal['preco_imovel'].min())}</strong> "
        f"e <strong>{fmt_brl(serie_mensal['preco_imovel'].max())}</strong>, sem uma tendência clara de alta ou de queda. "
        "Os picos e vales indicam <strong>ciclos curtos de aquecimento e retração</strong>, mas na base simulada eles não "
        "seguem um padrão sazonal consistente."
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # --- Gráfico 2: Evolução anual por região ---
    section("Valorização Anual por Região")

    serie_reg = (
        df_filtrado.groupby(["ano", "regiao"])["preco_imovel"]
        .mean().reset_index()
    )
    regioes_unicas = serie_reg["regiao"].unique()
    REGION_COLORS  = [ACCENT, ACCENT2, ACCENT3, GREEN, "#f59e0b", "#e9c46a"]

    fig, ax = plt.subplots(figsize=(13, 4.5))
    fig.patch.set_facecolor("#1b2b26")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
    for reg, cor in zip(regioes_unicas, REGION_COLORS):
        subset = serie_reg[serie_reg["regiao"] == reg].sort_values("ano")
        ax.plot(subset["ano"], subset["preco_imovel"],
                color=cor, linewidth=2, marker="o", markersize=5, label=reg)
    ax.legend(framealpha=0.15, labelcolor="white", fontsize=9)
    ax.set_title("Evolução do Preço Médio Anual por Região", pad=14)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Preço Médio (R$)")
    st.pyplot(fig, use_container_width=True)

    _m_reg = df_filtrado.groupby("regiao")["preco_imovel"].mean()
    insight(
        f"🗺️ <strong>{_m_reg.idxmax()}</strong> tem o maior preço médio e <strong>{_m_reg.idxmin()}</strong> o menor, "
        f"com diferença de <strong>{(_m_reg.max() / _m_reg.min() - 1) * 100:.1f}%</strong>. "
        "As diferenças regionais existem, mas são <strong>moderadas</strong> nesta base simulada."
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # --- Gráfico 3: Crescimento % cidades top ---
    section("Cidades com Maior Crescimento de Preço (Primeiro vs. Último Ano)")

    anos_disp = sorted(df_filtrado["ano"].unique())
    if len(anos_disp) >= 2:
        ano_ini, ano_fim = anos_disp[0], anos_disp[-1]
        preco_ini = df_filtrado[df_filtrado["ano"] == ano_ini].groupby("cidade")["preco_imovel"].mean()
        preco_fim = df_filtrado[df_filtrado["ano"] == ano_fim].groupby("cidade")["preco_imovel"].mean()
        crescimento = ((preco_fim - preco_ini) / preco_ini * 100).dropna().sort_values(ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(12, 4.5))
        fig.patch.set_facecolor("#1b2b26")
        bars = ax.barh(crescimento.index[::-1], crescimento.values[::-1], color=PALETTE_COOL[:10], height=0.6, zorder=3)
        for bar in bars: bar.set_linewidth(0)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_title(f"Top 10 Cidades — Crescimento de Preço ({ano_ini}→{ano_fim})", pad=12)
        ax.set_xlabel("Variação %")
        st.pyplot(fig, use_container_width=True)

        top_cidade_cres  = crescimento.index[0]
        top_perc_cres    = crescimento.iloc[0]
        insight(
            f"🚀 <strong>{top_cidade_cres}</strong> liderou a valorização no período analisado, "
            f"com crescimento de <strong>{top_perc_cres:.1f}%</strong>. "
            "Como cada cidade tem poucas observações por ano, esse crescimento é sensível a ruído "
            "e deve ser lido com cautela, não como tendência firme de mercado."
        )
    else:
        st.info("Selecione um intervalo de datas com ao menos dois anos para visualizar o crescimento por cidade.")

# ══════════════════════════════════════════════
#  ABA 2 — TIPOLOGIA E NÍVEIS
# ══════════════════════════════════════════════
with aba2:
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        section("Preço Médio por Tipo de Imóvel")
        preco_tipo = (
            df_filtrado.groupby("tipo_imovel")["preco_imovel"]
            .mean().sort_values(ascending=False).reset_index()
        )
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor("#1b2b26")
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
        bars = ax.bar(preco_tipo["tipo_imovel"], preco_tipo["preco_imovel"],
                      color=PALETTE_BLUE[:len(preco_tipo)], width=0.55, zorder=3)
        for bar in bars: bar.set_linewidth(0)
        ax.set_title("Precificação por Tipologia", pad=12)
        ax.set_xlabel("Tipo de Imóvel")
        ax.set_ylabel("Valor Médio")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig, use_container_width=True)

    with col_b:
        section("Concentração por Nível de Preço")
        volume_nivel = (
            df_filtrado.groupby("nivel_preco")["preco_imovel"]
            .count().reset_index()
            .rename(columns={"preco_imovel": "quantidade"})
            .sort_values("quantidade", ascending=False)
        )
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor("#1b2b26")
        bars = ax.bar(volume_nivel["nivel_preco"], volume_nivel["quantidade"],
                      color=PALETTE_PURP[:len(volume_nivel)], width=0.55, zorder=3)
        for bar in bars: bar.set_linewidth(0)
        ax.set_title("Volume de Imóveis por Categoria", pad=12)
        ax.set_xlabel("Nível de Preço")
        ax.set_ylabel("Quantidade de Imóveis")
        st.pyplot(fig, use_container_width=True)

    insight(
        f"🏠 <strong>{tipo_topo}</strong> é o tipo de imóvel com maior valor médio na seleção atual, mas a diferença "
        "entre os tipos é pequena. Nesta base simulada, o nível de preço (Baixo a Luxo) <strong>não acompanha o valor "
        "em reais</strong> do imóvel, então deve ser lido como uma categoria, e não como faixa de preço."
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # --- Preço médio por tipo e região (heatmap) ---
    section("Heatmap — Preço Médio por Região × Tipo de Imóvel")
    pivot_heat = (
        df_filtrado.groupby(["regiao", "tipo_imovel"])["preco_imovel"]
        .mean().unstack(fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(12, max(3, len(pivot_heat) * 0.9)))
    fig.patch.set_facecolor("#1b2b26")
    sns.heatmap(
        pivot_heat / 1_000, ax=ax,
        cmap="YlGn", linewidths=0.4, linecolor="#0f1b17",
        annot=True, fmt=".0f", annot_kws={"size": 9, "color": "#1b2b26"},
        cbar_kws={"label": "Preço médio (R$ mil)"},
    )
    ax.set_title("Distribuição Regional do Preço Médio por Tipologia (R$ mil)", pad=14)
    ax.set_xlabel("Tipo de Imóvel")
    ax.set_ylabel("Região")
    ax.tick_params(axis="x", rotation=30)
    ax.tick_params(axis="y", rotation=0)
    st.pyplot(fig, use_container_width=True)

    insight(
        "🔥 O heatmap cruza <strong>região e tipo de imóvel</strong>. Tons mais escuros indicam combinações de maior "
        "preço médio. As diferenças entre as células são pequenas, o que mostra um mercado simulado bastante homogêneo."
    )

# ══════════════════════════════════════════════
#  ABA 3 — ANÁLISE GEOGRÁFICA
# ══════════════════════════════════════════════
with aba3:
    # --- Top 10 cidades mais caras ---
    section("Top 10 Cidades com Imóveis mais Caros")
    preco_cidade = (
        df_filtrado.groupby(["cidade", "uf"])["preco_imovel"]
        .mean().sort_values(ascending=False).head(10).reset_index()
    )
    preco_cidade["Local"] = preco_cidade["cidade"] + "  ·  " + preco_cidade["uf"]

    fig, ax = plt.subplots(figsize=(11, 4.8))
    fig.patch.set_facecolor("#1b2b26")
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
    bars = ax.barh(preco_cidade["Local"][::-1], preco_cidade["preco_imovel"][::-1],
                   color=PALETTE_COOL[:10], height=0.6, zorder=3)
    for bar in bars: bar.set_linewidth(0)
    ax.set_title("Ranking de Valorização Municipal", pad=12)
    ax.set_xlabel("Preço Médio (R$)")
    ax.set_ylabel("")
    st.pyplot(fig, use_container_width=True)

    cidade_top = preco_cidade.iloc[0]["cidade"]
    preco_top  = preco_cidade.iloc[0]["preco_imovel"]
    st.success(
        f"🏆 A cidade mais cara na seleção atual é **{cidade_top}**, "
        f"com preço médio de **{fmt_brl(preco_top)}**."
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # --- Comparação regional por barras ---
    col_r1, col_r2 = st.columns(2, gap="large")

    with col_r1:
        section("Preço Médio por Região")
        preco_reg = (
            df_filtrado.groupby("regiao")["preco_imovel"]
            .mean().sort_values(ascending=False).reset_index()
        )
        fig, ax = plt.subplots(figsize=(6.5, 4))
        fig.patch.set_facecolor("#1b2b26")
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
        bars = ax.bar(preco_reg["regiao"], preco_reg["preco_imovel"],
                      color=PALETTE_COOL[:len(preco_reg)], width=0.55, zorder=3)
        for bar in bars: bar.set_linewidth(0)
        ax.set_title("Comparação Regional — Preço Médio", pad=12)
        ax.set_xlabel("Região")
        ax.set_ylabel("Preço Médio")
        ax.tick_params(axis="x", rotation=15)
        st.pyplot(fig, use_container_width=True)

    with col_r2:
        section("Renda Média por Região")
        renda_reg = (
            df_filtrado.groupby("regiao")["renda_media"]
            .mean().sort_values(ascending=False).reset_index()
        )
        fig, ax = plt.subplots(figsize=(6.5, 4))
        fig.patch.set_facecolor("#1b2b26")
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.1f}k'))
        bars = ax.bar(renda_reg["regiao"], renda_reg["renda_media"],
                      color=PALETTE_PURP[:len(renda_reg)], width=0.55, zorder=3)
        for bar in bars: bar.set_linewidth(0)
        ax.set_title("Comparação Regional — Renda Média", pad=12)
        ax.set_xlabel("Região")
        ax.set_ylabel("Renda Média")
        ax.tick_params(axis="x", rotation=15)
        st.pyplot(fig, use_container_width=True)

    insight(
        f"🗺️ <strong>{regiao_cara}</strong> lidera o ranking regional de preços. Ao comparar preço e renda média "
        "por região, <strong>não aparece uma relação clara</strong>: as regiões de maior renda não são, necessariamente, "
        "as de maior preço."
    )

# ══════════════════════════════════════════════
#  ABA 4 — CORRELAÇÕES
# ══════════════════════════════════════════════
with aba4:
    col_c1, col_c2 = st.columns(2, gap="large")

    with col_c1:
        # --- Dispersão Área × Preço ---
        section("Dispersão — Área (m²) × Preço do Imóvel")
        amostra = df_filtrado.sample(min(800, len(df_filtrado)), random_state=42)
        TIPO_CORES = {t: c for t, c in zip(sorted(amostra["tipo_imovel"].unique()), PALETTE_COOL)}

        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor("#1b2b26")
        for tipo, grupo in amostra.groupby("tipo_imovel"):
            ax.scatter(grupo["area_m2"], grupo["preco_imovel"],
                       label=tipo, alpha=0.55, s=22, color=TIPO_CORES.get(tipo, ACCENT),
                       edgecolors="none")
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
        ax.set_title("Relação Área × Preço por Tipo de Imóvel", pad=12)
        ax.set_xlabel("Área (m²)")
        ax.set_ylabel("Preço (R$)")
        ax.legend(framealpha=0.15, labelcolor="white", fontsize=8)
        st.pyplot(fig, use_container_width=True)

        corr_area = df_filtrado["area_m2"].corr(df_filtrado["preco_imovel"])
        insight(
            f"📐 A correlação entre área e preço é de <strong>{corr_area:.2f}</strong>. "
            f"Isso indica uma relação <strong>{descrever_corr(corr_area)}</strong>: "
            "nesta base simulada, a metragem explica muito pouco do preço do imóvel."
        )

    with col_c2:
        # --- Renda × Preço por região ---
        section("Relação Renda Média × Preço por Região")
        renda_preco = (
            df_filtrado.groupby("regiao")
            .agg(renda=("renda_media", "mean"), preco=("preco_imovel", "mean"))
            .reset_index()
        )
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor("#1b2b26")
        for i, row in renda_preco.iterrows():
            cor = PALETTE_COOL[i % len(PALETTE_COOL)]
            ax.scatter(row["renda"], row["preco"], s=160, color=cor, zorder=5, edgecolors="#1b2b26", linewidth=1.5)
            ax.annotate(row["regiao"], (row["renda"], row["preco"]),
                        textcoords="offset points", xytext=(8, 4),
                        fontsize=9, color="#e6efe9")
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.1f}k'))
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
        ax.set_title("Renda Média vs. Preço Médio por Região", pad=12)
        ax.set_xlabel("Renda Média Regional")
        ax.set_ylabel("Preço Médio do Imóvel")
        st.pyplot(fig, use_container_width=True)

        corr_renda = df_filtrado["renda_media"].corr(df_filtrado["preco_imovel"])
        insight(
            f"💵 A correlação entre renda e preço é de <strong>{corr_renda:.2f}</strong>. "
            f"Relação <strong>{descrever_corr(corr_renda)}</strong>: na teoria, maior renda sustentaria preços mais altos, "
            "mas esse efeito <strong>não aparece</strong> nesta base simulada."
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # --- Juros × Preço anual ---
    section("Impacto da Taxa de Juros no Preço Médio Anual")
    juros_preco = (
        df_filtrado.groupby("ano")
        .agg(preco=("preco_imovel", "mean"), juros=("taxa_juros", "mean"))
        .reset_index().sort_values("ano")
    )
    fig, ax1 = plt.subplots(figsize=(13, 4.5))
    fig.patch.set_facecolor("#1b2b26")
    ax2 = ax1.twinx()
    ax1.plot(juros_preco["ano"], juros_preco["preco"], color=ACCENT, linewidth=2.2,
             marker="o", markersize=6, label="Preço Médio", markeredgecolor="#1b2b26")
    ax2.plot(juros_preco["ano"], juros_preco["juros"], color="#e9c46a", linewidth=1.8,
             linestyle="--", marker="s", markersize=5, label="Taxa de Juros (%)", markeredgecolor="#1b2b26")
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R$ {x/1_000:.0f}k'))
    ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    ax2.tick_params(axis="y", colors="#e9c46a")
    ax2.yaxis.label.set_color("#e9c46a")
    ax1.set_title("Preço Médio Anual × Taxa de Juros (Eixo Duplo)", pad=14)
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Preço Médio (R$)")
    ax2.set_ylabel("Taxa de Juros (%)")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, framealpha=0.15, labelcolor="white", fontsize=9)
    st.pyplot(fig, use_container_width=True)

    corr_juros = df_filtrado["taxa_juros"].corr(df_filtrado["preco_imovel"])
    insight(
        f"📈 A correlação entre juros e preço é de <strong>{corr_juros:.2f}</strong> "
        f"(relação <strong>{descrever_corr(corr_juros)}</strong>). Na teoria, juros mais altos encarecem o crédito e "
        "pressionam os preços para baixo, mas essa relação <strong>não aparece</strong> nesta base simulada."
    )

# ══════════════════════════════════════════════
#  ABA — MAPAS INTERATIVOS (PLOTLY)
# ══════════════════════════════════════════════
CAMINHO_GEOJSON = BASE_DIR / "dados" / "brasil_estados.geojson"

@st.cache_data
def carregar_geojson():
    with open(CAMINHO_GEOJSON, encoding="utf-8") as f:
        return json.load(f)

ESCALA_TEAL = ["#d9f2ec", "#5eead4", "#14b8a6", "#0f766e"]

def estilo_plotly(fig, altura=520):
    """Aplica o tema escuro verde do dashboard a uma figura Plotly."""
    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1b2b26",
        font=dict(family="Inter, sans-serif", color="#e6efe9"),
        margin=dict(l=10, r=10, t=50, b=10),
        title=dict(font=dict(size=15)),
    )
    return fig

with aba_plotly:
    geojson_br = carregar_geojson()

    # ---------- 1. Mapa do Brasil por UF ----------
    section("Mapa do Brasil por Estado (UF)")
    metricas = {
        "Preço médio do imóvel (R$)": ("preco_imovel", "mean", "R$ {:,.0f}"),
        "Preço médio do m² (R$)":     ("preco_m2",     "mean", "R$ {:,.0f}"),
        "Renda média (R$)":           ("renda_media",  "mean", "R$ {:,.0f}"),
        "Taxa de juros média (%)":    ("taxa_juros",   "mean", "{:.2f}%"),
        "Quantidade de imóveis":      ("preco_imovel", "count", "{:,.0f}"),
    }
    metrica_nome = st.selectbox("Indicador exibido no mapa", list(metricas.keys()), key="metrica_mapa")
    coluna, agregacao, formato = metricas[metrica_nome]


    por_uf = (
        df_filtrado.groupby(["uf", "regiao"])[coluna].agg(agregacao).reset_index()
        .rename(columns={coluna: "valor"})
    )
    por_uf["valor_fmt"] = por_uf["valor"].apply(lambda v: formato.format(v).replace(",", "X").replace(".", ",").replace("X", "."))

    # Resumo completo de cada UF (aparece ao passar o mouse, seja qual for o indicador escolhido)
    resumo = df_filtrado.groupby("uf").agg(
        qtd=("preco_imovel", "count"), preco=("preco_imovel", "mean"), m2=("preco_m2", "mean"),
        renda=("renda_media", "mean"), juros=("taxa_juros", "mean"),
    ).reset_index()
    por_uf = por_uf.merge(resumo, on="uf")
    n = lambda v: f"{v:,.0f}".replace(",", ".")
    por_uf["detalhe"] = (
        "Região: " + por_uf["regiao"]
        + "<br>Imóveis: " + por_uf["qtd"].map(n)
        + "<br>Preço médio: R$ " + por_uf["preco"].map(n)
        + "<br>Preço do m²: R$ " + por_uf["m2"].map(n)
        + "<br>Renda média: R$ " + por_uf["renda"].map(n)
        + "<br>Juros médios: " + por_uf["juros"].map(lambda v: f"{v:.2f}".replace(".", ",")) + "%"
    )

    # Centro de cada estado (latitude, longitude), usado para escrever a sigla no mapa
    CENTROS = {
        "AC": (-9.3, -70.4), "AL": (-9.5, -36.6), "AM": (-4.2, -64.7), "AP": (1.4, -52.0),
        "BA": (-12.5, -41.7), "CE": (-5.1, -39.6), "DF": (-15.8, -47.8), "ES": (-19.6, -40.7),
        "GO": (-16.0, -49.6), "MA": (-5.1, -45.3), "MG": (-18.5, -44.7), "MS": (-20.3, -54.8),
        "MT": (-12.9, -55.9), "PA": (-4.0, -53.1), "PB": (-7.1, -36.8), "PE": (-8.3, -38.0),
        "PI": (-7.4, -43.0), "PR": (-24.6, -51.6), "RJ": (-22.2, -42.7), "RN": (-5.8, -36.7),
        "RO": (-10.9, -62.8), "RR": (2.1, -61.4), "RS": (-29.7, -53.3), "SC": (-27.2, -50.5),
        "SE": (-10.6, -37.4), "SP": (-22.3, -48.7), "TO": (-10.1, -48.3),
    }

    fig_mapa = px.choropleth(
        por_uf, geojson=geojson_br, locations="uf", featureidkey="properties.sigla",
        color="valor", labels={"valor": metrica_nome},
        color_continuous_scale=["#d4f1e8", "#9fe0cc", "#5cc7ab", "#2a9d8f"],  # só tons de verde
    )
    fig_mapa.update_traces(
        customdata=por_uf[["detalhe"]].values,
        hovertemplate="<b>%{location}</b><br>%{customdata[0]}<extra></extra>",
        marker_line_color="#0f1b17", marker_line_width=0.8,
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    ufs_mapa = [u for u in por_uf["uf"] if u in CENTROS]
    fig_mapa.add_trace(go.Scattergeo(  # sigla escrita dentro de cada estado
        lat=[CENTROS[u][0] for u in ufs_mapa], lon=[CENTROS[u][1] for u in ufs_mapa],
        text=ufs_mapa, mode="text", hoverinfo="skip", showlegend=False,
        textfont=dict(size=12, color="#0b1f1a", family="Inter, sans-serif"),
    ))
    fig_mapa.update_layout(coloraxis_colorbar=dict(title="", thickness=14, len=0.7))
    estilo_plotly(fig_mapa, altura=560)
    fig_mapa.update_layout(title=f"{metrica_nome} por UF")
    st.plotly_chart(fig_mapa, width="stretch")


    





    if len(por_uf) > 0:
        uf_alta = por_uf.loc[por_uf["valor"].idxmax()]
        uf_baixa = por_uf.loc[por_uf["valor"].idxmin()]
        insight(
            f"🗺️ Em <strong>{metrica_nome.lower()}</strong>, o maior valor está em <strong>{uf_alta['uf']}</strong> "
            f"({uf_alta['valor_fmt']}) e o menor em <strong>{uf_baixa['uf']}</strong> ({uf_baixa['valor_fmt']}). "
            "Passe o mouse sobre um estado para ver os detalhes. Estados sem dados na seleção atual ficam sem cor."
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ---------- 2. Animação por ano ----------
    section("Animação: Preço Médio por UF ao Longo dos Anos")
    anim = (
        df_filtrado.groupby(["ano", "uf"])["preco_imovel"].mean().reset_index()
        .sort_values(["ano", "preco_imovel"], ascending=[True, True])
    )
    if anim["ano"].nunique() >= 2:
        fig_anim = px.bar(
            anim, x="preco_imovel", y="uf", orientation="h", animation_frame="ano",
            color="preco_imovel", color_continuous_scale=ESCALA_TEAL,
            range_x=[0, anim["preco_imovel"].max() * 1.1],
            range_color=[anim["preco_imovel"].min(), anim["preco_imovel"].max()],
            labels={"preco_imovel": "Preço médio (R$)", "uf": "UF", "ano": "Ano"},
        )
        fig_anim.update_yaxes(categoryorder="total ascending", gridcolor="#2a4a42")
        fig_anim.update_xaxes(gridcolor="#2a4a42", tickprefix="R$ ", separatethousands=True)
        fig_anim.update_layout(coloraxis_showscale=False)
        estilo_plotly(fig_anim, altura=640)
        fig_anim.update_layout(title="Preço médio por UF — use o botão ▶ ou o controle deslizante de anos")
        st.plotly_chart(fig_anim, width="stretch")

        ano_ini, ano_fim = int(anim["ano"].min()), int(anim["ano"].max())
        insight(
            f"🎞️ A animação percorre os anos de <strong>{ano_ini}</strong> a <strong>{ano_fim}</strong>. "
            "O ranking das UFs muda de um ano para outro, mas os valores ficam em patamares próximos, "
            "o que confirma a <strong>estabilidade geral dos preços</strong> observada nas demais abas."
        )
    else:
        st.info("A animação precisa de pelo menos dois anos de dados. Amplie o período nos filtros.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ---------- 3. Treemap ----------
    section("Treemap: Região → UF → Cidade")
    arvore = (
        df_filtrado.groupby(["regiao", "uf", "cidade"])
        .agg(imoveis=("preco_imovel", "count"), preco_medio=("preco_imovel", "mean"))
        .reset_index()
    )
    fig_tree = px.treemap(
        arvore, path=[px.Constant("Brasil"), "regiao", "uf", "cidade"],
        values="imoveis", color="preco_medio", color_continuous_scale=ESCALA_TEAL,
        hover_data={"preco_medio": ":,.0f", "imoveis": True},
        labels={"preco_medio": "Preço médio (R$)", "imoveis": "Imóveis"},
    )
    fig_tree.update_traces(marker_line_color="#0f1b17", root_color="#1b2b26")
    fig_tree.update_layout(coloraxis_colorbar=dict(title="Preço<br>médio", thickness=14))
    estilo_plotly(fig_tree, altura=560)
    fig_tree.update_layout(title="Tamanho do bloco = nº de imóveis · Cor = preço médio")
    st.plotly_chart(fig_tree, width="stretch")

    insight(
        "🌳 O <strong>tamanho</strong> de cada bloco mostra quantos imóveis a base tem naquele local, e a "
        "<strong>cor</strong> mostra o preço médio. Clique em uma região para aprofundar até as cidades "
        "e clique no topo para voltar."
    )

# ══════════════════════════════════════════════
#  ABA 5 — CONSULTA SQL
# ══════════════════════════════════════════════
with aba5:
    section("Consulta SQL · SQLAlchemy &amp; SQLite")
    st.markdown(
        "<p style='color:#a3b8ad;font-size:0.9rem;margin-bottom:1rem'>"
        "Todos os dados foram persistidos automaticamente em um banco local "
        "(<code>mercado_imobiliario.sqlite</code>). "
        "O quadro abaixo é gerado via consulta SQL pura, demonstrando domínio de engenharia de dados."
        "</p>",
        unsafe_allow_html=True,
    )

    consulta = """\
SELECT regiao,
       tipo_imovel,
       COUNT(*)            AS qtd_imoveis,
       ROUND(AVG(preco_imovel), 2) AS media_preco,
       ROUND(AVG(renda_media),  2) AS renda_local,
       ROUND(AVG(taxa_juros),   2) AS juros_medio
FROM imoveis
GROUP BY regiao, tipo_imovel
ORDER BY media_preco DESC
LIMIT 15"""

    resultado_sql = pd.read_sql(consulta, engine)
    resultado_sql["media_preco"] = resultado_sql["media_preco"].apply(fmt_brl)
    resultado_sql["renda_local"] = resultado_sql["renda_local"].apply(fmt_brl)
    resultado_sql["juros_medio"] = resultado_sql["juros_medio"].apply(lambda x: f"{x:.2f}%")

    st.dataframe(resultado_sql, use_container_width=True, hide_index=True)
    st.code(consulta, language="sql")

# ══════════════════════════════════════════════
#  ABA 6 — BASE DE DADOS
# ══════════════════════════════════════════════
with aba6:
    section("Base de Dados Filtrada")
    st.caption(f"Exibindo **{len(df_filtrado):,}** registros com base nos filtros aplicados.")
    st.dataframe(df_filtrado, use_container_width=True)

# ─────────────────────────────────────────────
#  CONCLUSÃO EXECUTIVA — DINÂMICA (dados reais)
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# Cálculos para a conclusão
preco_ini_serie = preco_ano.iloc[0] if len(preco_ano) > 0 else 0
preco_fim_serie = preco_ano.iloc[-1] if len(preco_ano) > 0 else 0
var_total       = ((preco_fim_serie / preco_ini_serie) - 1) * 100 if preco_ini_serie > 0 else 0
tendencia       = "estabilidade" if abs(cagr) < 1 else ("valorização" if cagr > 0 else "queda")

regiao_mais_barata = (
    df_filtrado.groupby("regiao")["preco_imovel"].mean().idxmin()
)
diff_regioes = (
    df_filtrado.groupby("regiao")["preco_imovel"].mean().max() /
    df_filtrado.groupby("regiao")["preco_imovel"].mean().min()
)
nivel_disparidade = "moderadas" if (diff_regioes - 1) < 0.15 else "expressivas"

st.markdown(f"""
<div style="background:linear-gradient(135deg,#1b2b26,#0f1b17);border:1px solid rgba(94,234,212,0.15);
            border-radius:16px;padding:1.8rem 2.2rem;">
  <h4 style="color:#e6efe9;margin:0 0 1rem 0;font-size:1.15rem">
    📌 Conclusão Executiva
  </h4>

  <p style="color:#a3b8ad;font-size:0.9rem;line-height:1.8;margin:0 0 0.9rem 0">
    A análise do mercado imobiliário brasileiro entre <strong style="color:#5eead4">2015 e 2024</strong>
    evidencia <strong style="color:#e9c46a">{tendencia}</strong> dos preços: o preço médio nacional saiu de
    <strong style="color:#5eead4">{fmt_brl(preco_ini_serie)}</strong> para
    <strong style="color:#34d399">{fmt_brl(preco_fim_serie)}</strong>,
    uma variação de <strong style="color:#34d399">{var_total:.1f}%</strong> no período —
    equivalente a um crescimento médio anual de <strong style="color:#34d399">{cagr:.2f}% a.a.</strong>
  </p>

  <p style="color:#a3b8ad;font-size:0.9rem;line-height:1.8;margin:0 0 0.9rem 0">
    As <strong style="color:#5eead4">diferenças regionais</strong> são {nivel_disparidade}:
    a região <strong style="color:#e9c46a">{regiao_cara}</strong> lidera o ranking de preços,
    com ticket médio <strong style="color:#e9c46a">{(diff_regioes - 1) * 100:.1f}%</strong> superior ao da região
    <strong style="color:#e9c46a">{regiao_mais_barata}</strong>.
  </p>

  <p style="color:#a3b8ad;font-size:0.9rem;line-height:1.8;margin:0 0 0.9rem 0">
    Por tipologia, o segmento <strong style="color:#2dd4bf">{tipo_topo}</strong>
    apresenta o maior valor médio, embora a diferença entre os tipos seja pequena. A relação entre
    <strong style="color:#2dd4bf">renda e preço</strong>
    (correlação: <strong style="color:#2dd4bf">{corr_renda:.2f}</strong>) é
    <strong style="color:#2dd4bf">{descrever_corr(corr_renda)}</strong>, ou seja, nesta base a renda
    não explica o patamar de preços.
  </p>

  <p style="color:#a3b8ad;font-size:0.9rem;line-height:1.8;margin:0">
    Como os dados são <strong style="color:#e9c46a">simulados</strong>, os resultados devem ser lidos como um
    exercício metodológico: o dashboard permite cruzar <strong style="color:#e9c46a">juros</strong>, renda e
    evolução temporal, e a mesma análise pode ser aplicada a dados reais (como FipeZAP ou Banco Central).
    Nesta base, <strong style="color:#34d399">{cidade_cara}</strong> é a cidade de maior preço médio.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;color:#34483f;font-size:0.75rem;margin-top:1rem'>"
    "Fabiano dos Santos Gomes Bastos ImobiAnalytics · Dados simulados ·  Brasil 2015–2024 · Pandas · Seaborn · Matplotlib · Plotly · SQLAlchemy · NumPy"
    "</p>",
    unsafe_allow_html=True,
)
