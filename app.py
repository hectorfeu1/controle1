import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =====================================================
# CONFIGURAÇÕES
# =====================================================

NUM_PEDIDOS_MES = 10000
CUSTO_SITE_FIXO_MENSAL = 5000.0
CUSTOS_FIXOS_OPERACAO = 382 + 660 + 349 + 1945.38 + 17560 + 17000
CUSTO_FIXO_UNITARIO = (CUSTOS_FIXOS_OPERACAO + CUSTO_SITE_FIXO_MENSAL) / NUM_PEDIDOS_MES
CUSTO_OPERACIONAL_PEDIDO = 2.625

COMISSAO_FABI = 0.015
ARMAZENAGEM = 0.018

ICMS = 0.0125
DIFAL = 0.0655
PIS_COFINS = 0.0925
IMPOSTOS_TOTAL = ICMS + DIFAL + PIS_COFINS

marketplaces = {
    "Amazon": {"comissao": 0.15, "frete": 23},
    "Americanas": {"comissao": 0.17, "frete": 0.08},
    "Magalu": {"comissao": 0.148, "frete": 0.08},
    "Mercado Livre": {"comissao": 0.17, "frete": 23},
    "Olist": {"comissao": 0.19, "frete": 0.11},
    "Shopee": {"comissao": 0.14, "frete": 0},
}

# =====================================================
# CSS GRID PROFISSIONAL
# =====================================================

st.markdown("""
<style>

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 15px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 15px;
}

.card {
    padding: 18px;
    border-radius: 14px;
    background-color: var(--background-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.card-best { border-left: 6px solid #2563eb; }
.card-green { border-left: 6px solid #16a34a; }
.card-yellow { border-left: 6px solid #facc15; }
.card-red { border-left: 6px solid #dc2626; }

.kpi-title { font-size: 14px; opacity: 0.7; }
.kpi-value { font-size: 22px; font-weight: bold; }
.kpi-sub { font-size: 13px; opacity: 0.6; }

</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES
# =====================================================

def calcular_fabi(preco, custo):
    lucro = (
        preco
        - custo
        - CUSTO_FIXO_UNITARIO
        - CUSTO_OPERACIONAL_PEDIDO
        - preco * COMISSAO_FABI
        - preco * ARMAZENAGEM
        - preco * IMPOSTOS_TOTAL
    )
    return lucro, (lucro / preco) * 100


def calcular_marketplace(nome, preco, custo):
    taxa_extra = 0
    fixo_rateado = CUSTOS_FIXOS_OPERACAO / NUM_PEDIDOS_MES
    dados = marketplaces[nome]

    if nome == "Mercado Livre":
        comissao = preco * 0.17
        if preco < 79:
            taxa_extra = 6.75
        frete = 23

    elif nome == "Shopee":
        if preco <= 79.99:
            comissao = preco * 0.20
            taxa_extra = 4
        elif preco <= 99.99:
            comissao = preco * 0.14
            taxa_extra = 16
        else:
            comissao = preco * 0.14
            taxa_extra = 26
        frete = 0

    elif nome == "Amazon":
        comissao = preco * dados["comissao"]
        frete = 23

    else:
        comissao = preco * dados["comissao"]
        frete = preco * dados["frete"]

    impostos = preco * IMPOSTOS_TOTAL
    armazenagem = preco * ARMAZENAGEM

    custo_total = (
        custo
        + comissao
        + frete
        + impostos
        + armazenagem
        + fixo_rateado
        + CUSTO_OPERACIONAL_PEDIDO
        + taxa_extra
    )

    lucro = preco - custo_total
    margem = (lucro / preco) * 100

    return lucro, margem


# =====================================================
# CARREGAMENTO
# =====================================================

@st.cache_data
def carregar():
    df = pd.read_csv("dados.txt", sep="\t", encoding="utf-8")
    df = df.rename(columns={
        "Material": "sku",
        "DescricaoCompleta": "nome",
        "SubGrupo": "marca",
        "custoMedio": "custo_produto"
    })
    return df

df = carregar()

# =====================================================
# HEADER
# =====================================================

st.title("📊 Dashboard Estratégico de Margem")

col1, col2 = st.columns(2)

with col1:
    sku = st.text_input("Buscar SKU")

with col2:
    preco_venda = st.number_input("Preço de Venda", value=100.0)

if not sku:
    st.stop()

produto_df = df[df["sku"].astype(str).str.contains(sku, case=False)]

if produto_df.empty:
    st.warning("Produto não encontrado")
    st.stop()

produto = produto_df.iloc[0]

st.caption(f"{produto['nome']} | Marca: {produto['marca']} | Custo: R$ {produto['custo_produto']:.2f}")

# =====================================================
# LOJA FABI
# =====================================================

st.markdown('<div class="section-title">🏪 Loja FABI</div>', unsafe_allow_html=True)

lucro_fabi, margem_fabi = calcular_fabi(preco_venda, produto["custo_produto"])

classe_fabi = "card-green" if margem_fabi > 10 else "card-yellow" if margem_fabi > 0 else "card-red"

st.markdown(f"""
<div class="grid">
    <div class="card {classe_fabi}">
        <div class="kpi-title">Loja FABI</div>
        <div class="kpi-value">{margem_fabi:.2f}%</div>
        <div class="kpi-sub">Lucro: R$ {lucro_fabi:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MARKETPLACES GRID
# =====================================================

st.markdown('<div class="section-title">🛒 Marketplaces</div>', unsafe_allow_html=True)

resultados = []

for nome in marketplaces.keys():
    lucro, margem = calcular_marketplace(nome, preco_venda, produto["custo_produto"])
    resultados.append((nome, lucro, margem))

melhor = max(resultados, key=lambda x: x[2])[0]

cards_html = '<div class="grid">'

for nome, lucro, margem in resultados:

    if nome == melhor:
        classe = "card-best"
    elif margem > 10:
        classe = "card-green"
    elif margem > 0:
        classe = "card-yellow"
    else:
        classe = "card-red"

    cards_html += f"""
    <div class="card {classe}">
        <div class="kpi-title">{nome}</div>
        <div class="kpi-value">{margem:.2f}%</div>
        <div class="kpi-sub">Lucro: R$ {lucro:.2f}</div>
    </div>
    """

cards_html += "</div>"

st.markdown(cards_html, unsafe_allow_html=True)
