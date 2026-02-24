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
# ESTILO MINIMALISTA SOFISTICADO
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
    max-width: 1200px;
}

h1 {
    font-weight: 600;
    letter-spacing: -1px;
}

h2, h3 {
    font-weight: 500;
}

.stNumberInput input {
    background-color: #1c1f26;
    border-radius: 10px;
    border: 1px solid #2c2f36;
    color: white;
}

.stSelectbox div {
    background-color: #1c1f26 !important;
    border-radius: 10px !important;
}

.stMetric {
    background-color: #1c1f26;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #2c2f36;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border: 1px solid #2c2f36;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CONFIGURAÇÕES DE NEGÓCIO
# =====================================================

ARQUIVO_DADOS = "dados.txt"

NUM_PEDIDOS_MES = 10000
MARGEM_PADRAO = 20.0

CUSTO_SITE_FIXO_MENSAL = 5000.0
CUSTOS_FIXOS_OPERACAO = 382 + 660 + 349 + 1945.38 + 17560 + 17000

CUSTO_FIXO_UNITARIO = (CUSTOS_FIXOS_OPERACAO + CUSTO_SITE_FIXO_MENSAL) / NUM_PEDIDOS_MES
CUSTO_OPERACIONAL_PEDIDO = 2.625

COMISSAO = 0.015
ARMAZENAGEM = 0.018
IMPOSTOS = 0.0125 + 0.0655 + 0.0925

# =====================================================
# FUNÇÃO DE CARREGAMENTO
# =====================================================

@st.cache_data
def carregar_produtos():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Material","DescricaoCompleta","quantidade","custoMedio"])

    try:
        df = pd.read_csv(ARQUIVO_DADOS, sep="\t", encoding="utf-8")
    except:
        df = pd.read_csv(ARQUIVO_DADOS, sep="\t", encoding="latin1")

    df.columns = df.columns.str.strip()
    df["quantidade"] = pd.to_numeric(df.get("quantidade", 0), errors="coerce").fillna(0)
    df["custoMedio"] = pd.to_numeric(df.get("custoMedio", 0), errors="coerce").fillna(0)
    df["Material"] = df["Material"].astype(str)

    return df[df["quantidade"] > 0]

# =====================================================
# MOTOR DE PRECIFICAÇÃO
# =====================================================

def preco_minimo(custo, margem_percentual):
    return (
        (custo + CUSTO_FIXO_UNITARIO + CUSTO_OPERACIONAL_PEDIDO) /
        (1 - COMISSAO - ARMAZENAGEM - IMPOSTOS - margem_percentual/100)
    )

def margem_real(preco, custo):
    lucro = (
        preco
        - custo
        - CUSTO_FIXO_UNITARIO
        - CUSTO_OPERACIONAL_PEDIDO
        - preco * COMISSAO
        - preco * ARMAZENAGEM
        - preco * IMPOSTOS
    )
    return (lucro / preco) * 100

# =====================================================
# INTERFACE
# =====================================================

st.title("Precificação Inteligente - VTEX")
st.markdown("Fabricante Online")

st.markdown("---")

df = carregar_produtos()

if df.empty:
    st.warning("Nenhum produto ativo encontrado.")
else:
    sku = st.selectbox("Selecione o Produto (SKU)", df["Material"])
    produto = df[df["Material"] == sku].iloc[0]
    custo = float(produto["custoMedio"])

    col1, col2 = st.columns([1, 1.2])

    # =================================================
    # CARD PRODUTO
    # =================================================
    with col1:
        st.subheader("Produto")

        st.metric("Custo Médio", f"R$ {custo:,.2f}")
        st.metric("Custo Fixo Unitário", f"R$ {CUSTO_FIXO_UNITARIO:,.2f}")
        st.write(produto["DescricaoCompleta"])

    # =================================================
    # CARD SIMULAÇÃO
    # =================================================
    with col2:
        st.subheader("Simulação")

        margem_desejada = st.number_input(
            "Margem Desejada (%)",
            min_value=-50.0,
            max_value=100.0,
            value=MARGEM_PADRAO,
            step=0.5
        )

        preco_minimo_calc = preco_minimo(custo, margem_desejada)

        preco_input = st.number_input(
            "Preço de Venda (R$)",
            value=float(preco_minimo_calc),
            step=0.01
        )

        margem_calc = margem_real(preco_input, custo)

        st.metric("Preço Mínimo Sugerido", f"R$ {preco_minimo_calc:,.2f}")
        st.metric("Margem Líquida Real", f"{margem_calc:.2f}%")

        # =================================================
        # ALERTAS AUTOMÁTICOS
        # =================================================

        if margem_calc < 0:
            st.error("🔴 CRÍTICO — Produto está gerando prejuízo.")
        elif 0 <= margem_calc <= 5:
            st.warning("🟡 ATENÇÃO — Margem muito apertada.")
        else:
            st.success("🟢 EXCELENTE — Margem saudável.")

        # Barra visual de performance
        margem_visual = max(min(int(margem_calc), 100), 0)
        st.progress(margem_visual)

    # =================================================
    # DETALHAMENTO
    # =================================================

    with st.expander("Detalhamento do Cálculo"):
        st.write(f"Comissão: {COMISSAO*100:.2f}%")
        st.write(f"Armazenagem: {ARMAZENAGEM*100:.2f}%")
        st.write(f"Impostos Totais: {IMPOSTOS*100:.2f}%")
        st.write(f"Custo Operacional Pedido: R$ {CUSTO_OPERACIONAL_PEDIDO:.2f}")
        st.write(f"Custo Fixo Unitário: R$ {CUSTO_FIXO_UNITARIO:,.2f}")