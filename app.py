import streamlit as st

st.set_page_config(layout="wide")

# =========================
# DARK BI STYLE
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
    font-size: 26px;
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
# CUSTO BASE
# =========================
st.sidebar.header("⚙️ Configuração Produto")
custo = st.sidebar.number_input("Custo do Produto", value=10.00)

st.markdown("## 📊 Simulador de Precificação BI")

# =========================
# FUNÇÃO CALCULO
# =========================
def calcular_preco(custo, margem, comissao, taxa_fixa):
    preco = (custo + taxa_fixa) / (1 - (margem/100) - (comissao/100))
    return preco

# =========================
# MARKETPLACES
# =========================
col1, col2, col3 = st.columns(3)

# -------------------------
# MERCADO LIVRE
# -------------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🟡 Mercado Livre</div>', unsafe_allow_html=True)

    margem_ml = st.number_input("Margem % ML", value=30.0, key="ml1")
    comissao_ml = st.number_input("Comissão % ML", value=16.0, key="ml2")
    taxa_ml = st.number_input("Taxa Fixa ML", value=5.0, key="ml3")

    preco_ml = calcular_preco(custo, margem_ml, comissao_ml, taxa_ml)

    st.markdown(f'<div class="label">Preço Ideal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_ml:.2f}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# SHOPEE
# -------------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🟠 Shopee</div>', unsafe_allow_html=True)

    margem_sh = st.number_input("Margem % Shopee", value=35.0, key="sh1")
    comissao_sh = st.number_input("Comissão % Shopee", value=20.0, key="sh2")
    taxa_sh = st.number_input("Taxa Fixa Shopee", value=4.0, key="sh3")

    preco_sh = calcular_preco(custo, margem_sh, comissao_sh, taxa_sh)

    st.markdown(f'<div class="label">Preço Ideal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_sh:.2f}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# AMAZON
# -------------------------
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🔵 Amazon</div>', unsafe_allow_html=True)

    margem_am = st.number_input("Margem % Amazon", value=28.0, key="am1")
    comissao_am = st.number_input("Comissão % Amazon", value=15.0, key="am2")
    taxa_am = st.number_input("Taxa Fixa Amazon", value=6.0, key="am3")

    preco_am = calcular_preco(custo, margem_am, comissao_am, taxa_am)

    st.markdown(f'<div class="label">Preço Ideal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_am:.2f}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---")

# =========================
# LOJA FABI (REGRA DIFERENTE)
# =========================
st.markdown("## 🏪 Loja FABI (Venda Direta)")

col1, col2 = st.columns([2,1])

with col1:
    margem_fabi = st.number_input("Margem % Loja FABI", value=40.0)

with col2:
    preco_fabi = custo * (1 + margem_fabi/100)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">Preço Final</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi">R$ {preco_fabi:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
