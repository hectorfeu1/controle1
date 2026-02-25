import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Precificação Inteligente",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# ESTILO
# =====================================================

st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #0f1117;
    color: #EAEAEA;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

.stMetric {
    background-color: #1c1f26;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #2c2f36;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONFIGURAÇÕES DE NEGÓCIO
# =====================================================

ARQUIVO_DADOS = "dados.txt"
PEDIDOS_MES = 10000
MARGEM_PADRAO = 20.0

CANAIS = {
    "FABI": {"comissao": 0.015, "frete": 0, "armazenagem": 0.018},
    "Amazon": {"comissao": 0.15, "frete": 23},
    "Americanas": {"comissao": 0.17, "frete": 0.08},
    "Magalu": {"comissao": 0.148, "frete": 0.08},
    "Mercado Livre": {"comissao": 0.17, "frete": 23},
    "Olist": {"comissao": 0.19, "frete": 0.11},
    "Shopee": {"comissao": 0.14, "frete": 0},
}

CUSTOS_FIXOS_MENSAIS = 382 + 660 + 349 + 1945.38 + 17560 + 17000
CUSTO_SITE_FIXO_MENSAL = 5000
CUSTO_FIXO_UNITARIO = (CUSTOS_FIXOS_MENSAIS + CUSTO_SITE_FIXO_MENSAL) / PEDIDOS_MES
CUSTO_OPERACIONAL_PEDIDO = 2.625

ICMS = 0.0125
DIFAL = 0.0655
PIS_COFINS = 0.0925
IMPOSTOS_TOTAL = ICMS + DIFAL + PIS_COFINS

# =====================================================
# FUNÇÃO DE CARREGAMENTO
# =====================================================

@st.cache_data
def carregar_produtos():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Material","DescricaoCompleta","quantidade","custoMedio","Marca"])

    try:
        df = pd.read_csv(ARQUIVO_DADOS, sep="\t", encoding="utf-8")
    except:
        df = pd.read_csv(ARQUIVO_DADOS, sep="\t", encoding="latin1")

    df.columns = df.columns.str.strip()
    df["quantidade"] = pd.to_numeric(df.get("quantidade", 0), errors="coerce").fillna(0)
    df["custoMedio"] = pd.to_numeric(df.get("custoMedio", 0), errors="coerce").fillna(0)
    df["Material"] = df["Material"].astype(str)

    return df

# =====================================================
# INTERFACE
# =====================================================

st.title("Precificação Inteligente - Multi Canal")
st.markdown("Fabricante Online")
st.markdown("---")

df = carregar_produtos()

if df.empty:
    st.warning("Nenhum produto encontrado.")
else:
    sku = st.selectbox("Selecione o Produto (SKU)", df["Material"])
    produto = df[df["Material"] == sku].iloc[0]

    custo = float(produto["custoMedio"])
    estoque = int(produto["quantidade"])
    nome_produto = produto["DescricaoCompleta"]
    marca = produto.get("Marca", "Não informada")

    col1, col2 = st.columns([1, 2])

    # =================================================
    # CARD PRODUTO
    # =================================================

    with col1:
        st.subheader("Produto")

        st.markdown(f"**{marca}** | SKU {sku}")
        st.markdown(f"### {nome_produto}")

        st.metric("Custo Médio", f"R$ {custo:,.2f}")
        st.metric("Estoque Disponível", f"{estoque} un")

        if estoque <= 0:
            st.error("🔴 Sem estoque")
        elif estoque <= 10:
            st.warning("🟡 Estoque baixo")
        else:
            st.success("🟢 Estoque saudável")

    # =================================================
    # SIMULAÇÃO MULTI CANAL
    # =================================================

    with col2:
        st.subheader("Simulação por Canal")

        preco_venda_global = st.number_input(
            "Preço de Venda para Simulação (R$)",
            min_value=0.01,
            value=float(custo * 2),
            step=0.01
        )

        st.markdown("---")

        colunas = st.columns(3)

        for i, (nome, dados) in enumerate(CANAIS.items()):
            with colunas[i % 3]:

                st.markdown("""
                <div style="
                    border:1px solid #2c2f36;
                    border-radius:16px;
                    padding:18px;
                    background-color:#1c1f26;
                    margin-bottom:20px;">
                """, unsafe_allow_html=True)

                preco_venda = preco_venda_global
                taxa_extra = 0
                frete = 0

                # MERCADO LIVRE
                if nome == "Mercado Livre":

                    tipo_anuncio = st.selectbox(
                        "Tipo de anúncio",
                        options=["Clássico (12%)", "Premium (17%)"],
                        key=f"ml_{i}"
                    )

                    comissao_percentual = 0.12 if "Clássico" in tipo_anuncio else 0.17
                    comissao = preco_venda * comissao_percentual

                    if preco_venda < 79:
                        taxa_extra = 6.75

                    frete = 23

                # SHOPEE
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
                    elif preco_venda <= 499.99:
                        comissao = preco_venda * 0.14
                        taxa_extra = 26
                    else:
                        comissao = preco_venda * 0.14
                        taxa_extra = 26

                    frete = 0

                # AMAZON
                elif nome == "Amazon":
                    comissao = preco_venda * dados["comissao"]
                    frete = 23

                # OUTROS
                else:
                    comissao = preco_venda * dados["comissao"]

                    if dados["frete"] < 1:
                        frete = preco_venda * dados["frete"]
                    else:
                        frete = dados["frete"]

                impostos = preco_venda * IMPOSTOS_TOTAL
                armazenagem = preco_venda * dados.get("armazenagem", 0)

                custo_total = (
                    custo
                    + comissao
                    + frete
                    + impostos
                    + armazenagem
                    + CUSTO_FIXO_UNITARIO
                    + CUSTO_OPERACIONAL_PEDIDO
                    + taxa_extra
                )

                lucro = preco_venda - custo_total
                margem = (lucro / preco_venda) * 100

                if margem < 2:
                    status = "🔴 CRÍTICO"
                elif 2 <= margem <= 5:
                    status = "🟡 ATENÇÃO"
                else:
                    status = "🟢 EXCELENTE"

                st.markdown(f"### {nome}")
                st.metric("Margem Real", f"{margem:.2f}%")
                st.metric("Lucro por Unidade", f"R$ {lucro:,.2f}")
                st.write(status)

                margem_visual = max(min(int(margem), 100), 0)
                st.progress(margem_visual)

                st.markdown("</div>", unsafe_allow_html=True)
