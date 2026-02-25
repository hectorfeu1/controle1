import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =====================================================
# CONFIGURAÇÕES LOJA FABI
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


# =====================================================
# MARKETPLACES
# =====================================================

PEDIDOS_MES = 10000

marketplaces = {
    "Amazon": {"comissao": 0.15, "frete": 23},
    "Americanas": {"comissao": 0.17, "frete": 0.08},
    "Magalu": {"comissao": 0.148, "frete": 0.08},
    "Mercado Livre": {"comissao": 0.17, "frete": 23},
    "Olist": {"comissao": 0.19, "frete": 0.11},
    "Shopee": {"comissao": 0.14, "frete": 0},
}

custos_fixos_mensais = 382 + 660 + 349 + 1945.38 + 17560 + 17000
custos_operacionais_pedido = 2.625


# =====================================================
# FUNÇÕES LOJA FABI
# =====================================================

def preco_minimo_fabi(custo, margem_percentual):
    return (
        (custo + CUSTO_FIXO_UNITARIO + CUSTO_OPERACIONAL_PEDIDO)
        / (1 - COMISSAO_FABI - ARMAZENAGEM - IMPOSTOS_TOTAL - margem_percentual / 100)
    )


def margem_real_fabi(preco, custo):
    lucro = (
        preco
        - custo
        - CUSTO_FIXO_UNITARIO
        - CUSTO_OPERACIONAL_PEDIDO
        - preco * COMISSAO_FABI
        - preco * ARMAZENAGEM
        - preco * IMPOSTOS_TOTAL
    )
    return (lucro / preco) * 100


# =====================================================
# CARREGAMENTO DADOS
# =====================================================

@st.cache_data(show_spinner=False)
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

st.title("📊 Simulador Completo de Margem")

sku_busca = st.text_input("Buscar SKU")

if not sku_busca:
    st.stop()

produto_df = df_produtos[df_produtos["sku"].astype(str).str.contains(sku_busca, case=False)]

if produto_df.empty:
    st.warning("Produto não encontrado")
    st.stop()

produto = produto_df.iloc[0]

st.success(f"Produto: {produto['nome']}")
st.write(f"Custo: R$ {produto['custo_produto']:.2f}")

# =====================================================
# LOJA FABI
# =====================================================

st.header("🏪 Loja FABI")

preco_min = preco_minimo_fabi(produto["custo_produto"], MARGEM_PADRAO)

st.write(f"Preço mínimo para {MARGEM_PADRAO}%: R$ {preco_min:.2f}")

preco_venda = st.number_input("Preço de venda Loja FABI", value=float(preco_min))

margem_fabi = margem_real_fabi(preco_venda, produto["custo_produto"])

st.metric("Margem Real FABI", f"{margem_fabi:.2f}%")


# =====================================================
# MARKETPLACES
# =====================================================

if preco_venda > 0:

    st.header("🛒 Margem por Marketplace")

    fixo_rateado = custos_fixos_mensais / PEDIDOS_MES

    for nome, dados in marketplaces.items():

        taxa_extra = 0

        # Mercado Livre
        if nome == "Mercado Livre":

            tipo_anuncio = st.selectbox(
                "Tipo anúncio Mercado Livre",
                ["Classico", "Premium"],
                key="ml_tipo"
            )

            if tipo_anuncio == "Classico":
                comissao = preco_venda * 0.12
            else:
                comissao = preco_venda * 0.17

            if preco_venda < 79:
                taxa_extra = 6.75

            frete = 23

        # Shopee
        elif nome == "Shopee":

            if preco_venda <= 79.99:
                comissao = preco_venda * 0.20
                taxa_extra = 4
            elif preco_venda <= 99.99:
                comissao = preco_venda * 0.14
                taxa_extra = 16
            elif preco_venda <= 199.99:
                comissao = preco_venda * 0.14
                taxa_extra = 20
            else:
                comissao = preco_venda * 0.14
                taxa_extra = 26

            frete = 0

        # Amazon
        elif nome == "Amazon":
            comissao = preco_venda * dados["comissao"]
            frete = 23

        # Outros
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
            + custos_operacionais_pedido
            + taxa_extra
        )

        lucro = preco_venda - custo_total
        margem = (lucro / preco_venda) * 100

        st.write(f"### {nome}")
        st.write(f"Margem: {margem:.2f}%")
        st.write(f"Lucro por unidade: R$ {lucro:.2f}")
        st.divider()
