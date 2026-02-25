import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =====================================================
# CONFIGURAÇÕES GERAIS
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
# CSS CARDS
# =====================================================

st.markdown("""
<style>
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 18px;
}
.card {
    padding: 20px;
    border-radius: 16px;
    background-color: var(--background-color);
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.title { font-size: 16px; font-weight: 600; margin-bottom: 10px; }
.metric { font-size: 22px; font-weight: bold; }
.sub { font-size: 13px; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES DE PREÇO IDEAL
# =====================================================

def preco_ideal_fabi(custo, margem):
    return (
        (custo + CUSTO_FIXO_UNITARIO + CUSTO_OPERACIONAL_PEDIDO)
        / (1 - COMISSAO_FABI - ARMAZENAGEM - IMPOSTOS_TOTAL - margem/100)
    )

def preco_ideal_marketplace(nome, custo, margem):

    dados = marketplaces[nome]
    fixo_rateado = CUSTOS_FIXOS_OPERACAO / NUM_PEDIDOS_MES

    if nome == "Amazon":
        taxa_percentual = dados["comissao"] + IMPOSTOS_TOTAL + ARMAZENAGEM
        taxa_fixa = dados["frete"] + fixo_rateado + CUSTO_OPERACIONAL_PEDIDO

    elif nome in ["Americanas", "Magalu", "Olist"]:
        taxa_percentual = dados["comissao"] + dados["frete"] + IMPOSTOS_TOTAL + ARMAZENAGEM
        taxa_fixa = fixo_rateado + CUSTO_OPERACIONAL_PEDIDO

    elif nome == "Mercado Livre":
        taxa_percentual = 0.17 + IMPOSTOS_TOTAL + ARMAZENAGEM
        taxa_fixa = 23 + fixo_rateado + CUSTO_OPERACIONAL_PEDIDO

    elif nome == "Shopee":
        taxa_percentual = 0.14 + IMPOSTOS_TOTAL + ARMAZENAGEM
        taxa_fixa = fixo_rateado + CUSTO_OPERACIONAL_PEDIDO + 26

    return (custo + taxa_fixa) / (1 - taxa_percentual - margem/100)

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

st.title("📊 Simulador Estratégico de Preço")

col1, col2 = st.columns(2)

with col1:
    sku = st.text_input("Buscar SKU")

with col2:
    margem_desejada = st.number_input("Margem desejada (%)", value=20.0)

if not sku:
    st.stop()

produto_df = df[df["sku"].astype(str).str.contains(sku, case=False)]

if produto_df.empty:
    st.warning("Produto não encontrado")
    st.stop()

produto = produto_df.iloc[0]

st.caption(f"{produto['nome']} | Marca: {produto['marca']} | Custo: R$ {produto['custo_produto']:.2f}")

# =====================================================
# GRID DE CARDS
# =====================================================

cards_html = '<div class="grid">'

# Loja FABI
preco_fabi = preco_ideal_fabi(produto["custo_produto"], margem_desejada)

cards_html += f"""
<div class="card">
    <div class="title">🏪 Loja FABI</div>
    <div class="metric">R$ {preco_fabi:.2f}</div>
    <div class="sub">Preço necessário para {margem_desejada:.1f}%</div>
</div>
"""

# Marketplaces
for nome in marketplaces.keys():
    preco = preco_ideal_marketplace(nome, produto["custo_produto"], margem_desejada)

    cards_html += f"""
    <div class="card">
        <div class="title">🛒 {nome}</div>
        <div class="metric">R$ {preco:.2f}</div>
        <div class="sub">Preço necessário para {margem_desejada:.1f}%</div>
    </div>
    """

cards_html += "</div>"

st.markdown(cards_html, unsafe_allow_html=True)
