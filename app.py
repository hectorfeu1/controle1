import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# CSS DARK BI
# =========================
st.markdown("""
<style>

body {
    background-color: #0e1117;
}

.main {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: #1c1f26;
    padding: 25px;
    border-radius: 14px;
    border: 1px solid #2a2f3a;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

.title {
    font-size: 18px;
    font-weight: bold;
    color: white;
    margin-bottom: 15px;
}

.kpi {
    font-size: 28px;
    font-weight: bold;
    color: #00e676;
}

.label {
    color: #9aa4b2;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÃO DE CARGA OTIMIZADA
# =========================
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados.txt", sep="\t")
    return df

df = carregar_dados()

# =========================
# SIDEBAR PRODUTO
# =========================
st.sidebar.header("📦 Seleção de Produto")

produto = st.sidebar.selectbox(
    "Escolha o Produto",
    df["DescricaoCompleta"]
)

dados_produto = df[df["DescricaoCompleta"] == produto].iloc[0]

custo = float(dados_produto["custoMedio"])

st.sidebar.markdown(f"**Custo Médio:** R$ {custo:.2f}")
st.sidebar.markdown(f"**Estoque:** {int(dados_produto['quantidade'])}")

# =========================
# FUNÇÃO CALCULO
# =========================
def calcular_preco(custo, margem, comissao, taxa_fixa):
    return (custo + taxa_fixa) / (1 - (margem/100) - (comissao/100))

st.title("📊 Simulador BI de Precificação")

# =========================
# MARKETPLACES GRID
# =========================
col1, col2, col3 = st.columns(3)

# -------- Mercado Livre --------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🟡 Mercado Livre</div>', unsafe_allow_html=True)

    margem_ml = st.number_input("Margem %", value=30.0, key="ml_m")
    comissao_ml = st.number_input("Comissão %", value=16.0, key="ml_c")
    taxa_ml = st.number_input("Taxa Fixa", value=5.0, key="ml_t")

    preco_ml = calcular_preco(custo, margem_ml, comissao_ml, taxa_ml)

    st.markdown('<div class="label">Preço Ideal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_ml:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Shopee --------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🟠 Shopee</div>', unsafe_allow_html=True)

    margem_sh = st.number_input("Margem % ", value=35.0, key="sh_m")
    comissao_sh = st.number_input("Comissão % ", value=20.0, key="sh_c")
    taxa_sh = st.number_input("Taxa Fixa ", value=4.0, key="sh_t")

    preco_sh = calcular_preco(custo, margem_sh, comissao_sh, taxa_sh)

    st.markdown('<div class="label">Preço Ideal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_sh:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Amazon --------
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🔵 Amazon</div>', unsafe_allow_html=True)

    margem_am = st.number_input("Margem %  ", value=28.0, key="am_m")
    comissao_am = st.number_input("Comissão %  ", value=15.0, key="am_c")
    taxa_am = st.number_input("Taxa Fixa  ", value=6.0, key="am_t")

    preco_am = calcular_preco(custo, margem_am, comissao_am, taxa_am)

    st.markdown('<div class="label">Preço Ideal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_am:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# LOJA FABI
# =========================
st.subheader("🏪 Loja FABI (Venda Direta)")

col1, col2 = st.columns([2,1])

with col1:
    margem_fabi = st.number_input("Margem % Loja FABI", value=40.0)

with col2:
    preco_fabi = custo * (1 + margem_fabi/100)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">Preço Final</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_fabi:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# COMPARATIVO FINAL
# =========================
st.markdown("## 📈 Comparativo Geral")

comparativo = pd.DataFrame({
    "Marketplace": ["Mercado Livre", "Shopee", "Amazon", "Loja FABI"],
    "Preço Sugerido": [preco_ml, preco_sh, preco_am, preco_fabi]
})

st.dataframe(comparativo, use_container_width=True)
