import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Maquina de Precificação",
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
    max-width: 1400px;
}

.stMetric {
    background-color: #1c1f26;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #2c2f36;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CONFIGURAÇÕES DE NEGÓCIO
# =====================================================

ARQUIVO_DADOS = "dados.txt"
MARGEM_PADRAO = 20.0
PEDIDOS_MES = 10000

CANAIS = {
    "FABI": {"comissao": 0.015, "frete": 0, "armazenagem": 0.018},
    "Amazon": {"comissao": 0.15, "frete": 23, "armazenagem": 0},
    "Americanas": {"comissao": 0.17, "frete": 0.08, "armazenagem": 0},
    "Magalu": {"comissao": 0.148, "frete": 0.08, "armazenagem": 0},
    "Mercado Livre": {"comissao": 0.17, "frete": 23, "armazenagem": 0},
    "Olist": {"comissao": 0.19, "frete": 0.11, "armazenagem": 0},
    "Shopee": {"comissao": 0.14, "frete": 0, "armazenagem": 0},
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

    return df[df["quantidade"] >= 0]

# =====================================================
# MOTOR DE PRECIFICAÇÃO
# =====================================================

def calcular_taxas(preco, canal):
    taxas = CANAIS[canal]

    comissao = preco * taxas["comissao"]

    if taxas["frete"] < 1:
        frete = preco * taxas["frete"]
    else:
        frete = taxas["frete"]

    armazenagem = preco * taxas.get("armazenagem", 0)
    impostos = preco * IMPOSTOS_TOTAL

    return comissao + frete + armazenagem + impostos


def preco_minimo(custo, margem_percentual, canal):
    taxas = CANAIS[canal]

    percentual_total = (
        taxas["comissao"]
        + taxas.get("armazenagem", 0)
        + IMPOSTOS_TOTAL
        + margem_percentual / 100
    )

    frete_fixo = taxas["frete"] if taxas["frete"] >= 1 else 0

    return (
        (custo + CUSTO_FIXO_UNITARIO + CUSTO_OPERACIONAL_PEDIDO + frete_fixo)
        / (1 - percentual_total)
    )


def margem_real(preco, custo, canal):
    total_taxas = calcular_taxas(preco, canal)

    lucro = (
        preco
        - custo
        - CUSTO_FIXO_UNITARIO
        - CUSTO_OPERACIONAL_PEDIDO
        - total_taxas
    )

    return (lucro / preco) * 100


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

        margem_desejada = st.number_input(
            "Margem Desejada (%)",
            min_value=-50.0,
            max_value=100.0,
            value=MARGEM_PADRAO,
            step=0.5
        )

        st.markdown("---")

        colunas = st.columns(3)

        for i, canal in enumerate(CANAIS.keys()):
            with colunas[i % 3]:

                preco_min = preco_minimo(custo, margem_desejada, canal)
                margem_calc = margem_real(preco_min, custo, canal)

                st.markdown(f"### {canal}")
                st.metric("Preço Mínimo", f"R$ {preco_min:,.2f}")
                st.metric("Margem Líquida", f"{margem_calc:.2f}%")

                if margem_calc < 0:
                    st.error("🔴 Prejuízo")
                elif margem_calc <= 5:
                    st.warning("🟡 Margem baixa")
                else:
                    st.success("🟢 Saudável")

                margem_visual = max(min(int(margem_calc), 100), 0)
                st.progress(margem_visual)

                st.markdown("---")
