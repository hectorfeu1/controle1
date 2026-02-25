import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Precificação Estratégica",
    layout="wide"
)

# =====================================================
# ESTILO DASHBOARD
# =====================================================

st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #f4f6f9;
}

.kpi-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    border: 1px solid #e6e9ef;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONFIGURAÇÕES DE NEGÓCIO
# =====================================================

ARQUIVO_DADOS = "dados.txt"
PEDIDOS_MES = 10000

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

IMPOSTOS_TOTAL = 0.0125 + 0.0655 + 0.0925

# =====================================================
# CARREGAMENTO
# =====================================================

@st.cache_data
def carregar():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Material","DescricaoCompleta","quantidade","custoMedio","Marca"])
    df = pd.read_csv(ARQUIVO_DADOS, sep="\t")
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)
    df["custoMedio"] = pd.to_numeric(df["custoMedio"], errors="coerce").fillna(0)
    return df

df = carregar()

# =====================================================
# HEADER KPI
# =====================================================

st.title("📊 Dashboard de Precificação")

if df.empty:
    st.warning("Sem dados.")
    st.stop()

sku = st.selectbox("Selecionar SKU", df["Material"])
produto = df[df["Material"] == sku].iloc[0]

custo = float(produto["custoMedio"])
estoque = int(produto["quantidade"])
marca = produto.get("Marca", "Não informada")

preco_simulado = st.number_input(
    "Preço de Venda Simulado",
    min_value=0.01,
    value=custo * 2,
    step=0.01
)

# =====================================================
# KPI SUPERIOR
# =====================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Custo Produto", f"R$ {custo:,.2f}")
col2.metric("Estoque", f"{estoque} un")
col3.metric("Custo Fixo Unit.", f"R$ {CUSTO_FIXO_UNITARIO:,.2f}")
col4.metric("Preço Simulado", f"R$ {preco_simulado:,.2f}")

st.markdown("---")

# =====================================================
# MARKETPLACES EM GRID ORGANIZADO
# =====================================================

st.subheader("Rentabilidade por Canal")

grid = st.columns(3)

for i, (nome, dados) in enumerate(CANAIS.items()):
    with grid[i % 3]:

        taxa_extra = 0
        frete = 0

        # Mercado Livre
        if nome == "Mercado Livre":
            tipo = st.selectbox(
                f"Tipo ML",
                ["Clássico 12%", "Premium 17%"],
                key=f"ml_{i}"
            )
            comissao = preco_simulado * (0.12 if "Clássico" in tipo else 0.17)
            if preco_simulado < 79:
                taxa_extra = 6.75
            frete = 23

        # Shopee
        elif nome == "Shopee":
            if preco_simulado <= 79.99:
                comissao = preco_simulado * 0.20
                taxa_extra = 4
            elif preco_simulado <= 99.99:
                comissao = preco_simulado * 0.14
                taxa_extra = 16
            else:
                comissao = preco_simulado * 0.14
                taxa_extra = 26
            frete = 0

        # Outros
        else:
            comissao = preco_simulado * dados["comissao"]
            frete = dados["frete"] if dados["frete"] >= 1 else preco_simulado * dados["frete"]

        impostos = preco_simulado * IMPOSTOS_TOTAL
        armazenagem = preco_simulado * dados.get("armazenagem", 0)

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

        lucro = preco_simulado - custo_total
        margem = (lucro / preco_simulado) * 100

        # Card estilo executivo
        st.markdown(f"""
        <div class="kpi-card">
            <h4>{nome}</h4>
            <p><b>Margem:</b> {margem:.2f}%</p>
            <p><b>Lucro:</b> R$ {lucro:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
