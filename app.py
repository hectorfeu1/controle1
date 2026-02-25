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
# CSS ESTILO BI
# =====================================================

st.markdown("""
<style>

.kpi-card {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(135deg, #1e293b, #0f172a);
    color: white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    margin-bottom: 25px;
}

.kpi-title {
    font-size: 16px;
    opacity: 0.8;
}

.kpi-value {
    font-size: 36px;
    font-weight: bold;
    margin-top: 5px;
}

.market-card {
    padding: 18px;
    border-radius: 16px;
    background-color: var(--background-color);
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    text-align: center;
}

.market-title {
    font-size: 14px;
    opacity: 0.7;
}

.market-value {
    font-size: 24px;
    font-weight: bold;
    margin-top: 8px;
}

.market-sub {
    font-size: 12px;
    opacity: 0.6;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES
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

st.title("📊 Dashboard Estratégico de Preço")

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
# KPI PRINCIPAL – LOJA FABI
# =====================================================

preco_fabi = preco_ideal_fabi(produto["custo_produto"], margem_desejada)

st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">🏪 Loja FABI - Preço Ideal</div>
    <div class="kpi-value">R$ {preco_fabi:.2f}</div>
    <div>Margem alvo: {margem_desejada:.1f}%</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MARKETPLACES LADO A LADO
# =====================================================

st.markdown('<div class="section-title">🛒 Marketplaces</div>', unsafe_allow_html=True)

cols = st.columns(len(marketplaces))

for i, nome in enumerate(marketplaces.keys()):

    preco = preco_ideal_marketplace(nome, produto["custo_produto"], margem_desejada)

    with cols[i]:
        st.markdown(f"""
        <div class="market-card">
            <div class="market-title">{nome}</div>
            <div class="market-value">R$ {preco:.2f}</div>
            <div class="market-sub">Preço para {margem_desejada:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
