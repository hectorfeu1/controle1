import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =====================================================
# CONFIGURAÇÕES
# =====================================================

NUM_PEDIDOS_MES = 10000
MARGEM_PADRAO = 20.0

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
# CSS DASHBOARD
# =====================================================

st.markdown("""
<style>
.card {
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
    background-color: var(--background-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
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

def margem_fabi(preco, custo):
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

# =====================================================
# CARREGAMENTO
# =====================================================

@st.cache_data
def carregar_produtos():
    df = pd.read_csv("dados.txt", sep="\t", encoding="utf-8")
    df = df.rename(columns={
        "Material": "sku",
        "DescricaoCompleta": "nome",
        "SubGrupo": "marca",
        "custoMedio": "custo_produto"
    })
    return df

df_produtos = carregar_produtos()

# =====================================================
# TÍTULO
# =====================================================

st.title("📊 Simulador Estratégico de Margem")

col1, col2 = st.columns(2)

with col1:
    busca_sku = st.text_input("🔎 Buscar SKU")

with col2:
    preco_venda = st.number_input("💰 Preço de Venda", value=100.0)

if not busca_sku:
    st.stop()

produto_df = df_produtos[df_produtos["sku"].astype(str).str.contains(busca_sku, case=False)]

if produto_df.empty:
    st.warning("Produto não encontrado")
    st.stop()

produto = produto_df.iloc[0]

st.subheader(f"{produto['nome']} ({produto['sku']})")
st.caption(f"Marca: {produto['marca']} | Custo: R$ {produto['custo_produto']:.2f}")

# =====================================================
# CARDS
# =====================================================

st.markdown("---")

canais = ["Loja FABI"] + list(marketplaces.keys())
cols = st.columns(len(canais))

for i, canal in enumerate(canais):

    with cols[i]:

        taxa_extra = 0

        if canal == "Loja FABI":

            lucro, margem = margem_fabi(preco_venda, produto["custo_produto"])

        else:

            dados = marketplaces[canal]
            fixo_rateado = CUSTOS_FIXOS_OPERACAO / NUM_PEDIDOS_MES

            # Mercado Livre
            if canal == "Mercado Livre":
                tipo = st.selectbox(
                    f"Tipo ML",
                    ["Classico", "Premium"],
                    key="ml_tipo"
                )
                comissao = preco_venda * (0.12 if tipo == "Classico" else 0.17)
                if preco_venda < 79:
                    taxa_extra = 6.75
                frete = 23

            # Shopee
            elif canal == "Shopee":
                if preco_venda <= 79.99:
                    comissao = preco_venda * 0.20
                    taxa_extra = 4
                elif preco_venda <= 99.99:
                    comissao = preco_venda * 0.14
                    taxa_extra = 16
                else:
                    comissao = preco_venda * 0.14
                    taxa_extra = 26
                frete = 0

            elif canal == "Amazon":
                comissao = preco_venda * dados["comissao"]
                frete = 23

            else:
                comissao = preco_venda * dados["comissao"]
                frete = preco_venda * dados["frete"]

            impostos = preco_venda * IMPOSTOS_TOTAL
            armazenagem = preco_venda * ARMAZENAGEM

            custo_total = (
                produto["custo_produto"]
                + comissao
                + frete
                + impostos
                + armazenagem
                + fixo_rateado
                + CUSTO_OPERACIONAL_PEDIDO
                + taxa_extra
            )

            lucro = preco_venda - custo_total
            margem = (lucro / preco_venda) * 100

        # Cor do card
        if margem > 10:
            classe = "card-green"
        elif margem > 0:
            classe = "card-yellow"
        else:
            classe = "card-red"

        st.markdown(f"""
        <div class="card {classe}">
            <div class="kpi-title">{canal}</div>
            <div class="kpi-value">{margem:.2f}%</div>
            <div class="kpi-sub">Lucro: R$ {lucro:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
