import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")

# ==============================
# CONFIGURAÇÕES GERAIS
# ==============================

NUM_PEDIDOS_MES = 10000

CUSTO_SITE_FIXO_MENSAL = 5000.0
CUSTOS_FIXOS_OPERACAO = 382 + 660 + 349 + 1945.38 + 17560 + 17000
CUSTO_FIXO_UNITARIO = (CUSTOS_FIXOS_OPERACAO + CUSTO_SITE_FIXO_MENSAL) / NUM_PEDIDOS_MES

CUSTOS_OPERACIONAIS_PEDIDO = 2.625

COMISSAO_SITE = 0.015
ARMAZENAGEM = 0.018

ICMS = 0.0125
DIFAL = 0.0655
PIS_COFINS = 0.0925
IMPOSTOS_TOTAL = ICMS + DIFAL + PIS_COFINS

# ==============================
# DESIGN EXECUTIVO
# ==============================

st.markdown("""
<style>
body {background-color: #0f172a;}
.block-container {padding-top: 2rem;}
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #334155;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    text-align: center;
}
.market-title {
    font-weight: 600;
    font-size: 18px;
    color: #f1f5f9;
}
.margin {
    font-size: 24px;
    font-weight: bold;
}
.negative {color: #ef4444;}
.positive {color: #22c55e;}
</style>
""", unsafe_allow_html=True)

st.title("Maquina de Precificação")

# ==============================
# UPLOAD ARQUIVO
# ==============================

uploaded_file = st.file_uploader(
    "Upload arquivo TXT ou CSV",
    type=["csv", "txt"]
)

if uploaded_file:

    def carregar_arquivo(file):
        content = file.read()

        for enc in ["utf-8", "latin1", "cp1252"]:
            try:
                text = content.decode(enc)
                break
            except:
                continue

        for sep in ["\t", ";", ","]:
            try:
                df = pd.read_csv(io.StringIO(text), sep=sep)
                if len(df.columns) > 3:
                    return df
            except:
                continue

        return None

    df = carregar_arquivo(uploaded_file)

    if df is None:
        st.error("❌ Não foi possível interpretar o arquivo.")
        st.stop()

    df.columns = df.columns.str.strip()

    # Renomeia seu padrão ERP automaticamente
    if "Material" in df.columns:
        df = df.rename(columns={
            "Material": "sku",
            "DescricaoCompleta": "nome",
            "custoMedio": "custo_produto",
            "quantidade": "estoque"
        })

    df["custo_produto"] = pd.to_numeric(df["custo_produto"], errors="coerce")
    df = df.dropna(subset=["custo_produto"])

    st.success(f"✅ {len(df)} produtos carregados.")

    # ==============================
    # SELEÇÃO PRODUTO
    # ==============================

    sku = st.selectbox("Selecione o SKU", df["sku"].astype(str))
    produto = df[df["sku"].astype(str) == sku].iloc[0]

    custo_produto = produto["custo_produto"]

    st.markdown(f"### {produto['nome']}")
    st.write(f"💰 Custo Produto: R$ {custo_produto:.2f}")

    preco_venda = st.number_input(
        "Digite o preço de venda (R$)",
        min_value=0.01,
        format="%.2f"
    )

    # ==============================
    # FUNÇÕES PADRONIZADAS
    # ==============================

    def calcular_margem(preco, custo_total):
        lucro = preco - custo_total
        return (lucro / preco) * 100

    def custo_base(preco, comissao_percentual, frete_fixo=0, frete_percentual=0, taxa_extra=0):
        percentual_total = comissao_percentual + IMPOSTOS_TOTAL + ARMAZENAGEM
        return (
            custo_produto
            + preco * percentual_total
            + frete_fixo
            + preco * frete_percentual
            + taxa_extra
            + CUSTO_FIXO_UNITARIO
            + CUSTOS_OPERACIONAIS_PEDIDO
        )

    # ==============================
    # RESULTADOS
    # ==============================

  

    st.markdown("## Margem por Canal")

# ==============================
# CONFIGURAÇÕES EXTRAS
# ==============================

tipo_ml = st.selectbox("Tipo de anúncio Mercado Livre", ["Classico", "Premium"])

# ==============================
# FUNÇÃO PADRÃO
# ==============================

def calcular_canal(nome, preco, comissao, frete_fixo=0, frete_percentual=0, taxa_extra=0):
    percentual_total = comissao + IMPOSTOS_TOTAL + ARMAZENAGEM
    custo_percentual = preco * percentual_total

    custo_total = (
        custo_produto
        + custo_percentual
        + frete_fixo
        + preco * frete_percentual
        + taxa_extra
        + CUSTO_FIXO_UNITARIO
        + CUSTOS_OPERACIONAIS_PEDIDO
    )

    lucro = preco - custo_total
    margem = (lucro / preco) * 100

    return margem, custo_total, lucro

def card(nome, margem):
    cor = "#22c55e" if margem >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="card">
        <div class="market-title">{nome}</div>
        <div class="margin" style="color:{cor}">
            {margem:.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# CÁLCULOS
# ==============================

m_site, ct_site, l_site = calcular_canal("Site", preco_venda, COMISSAO_SITE)
m_amazon, ct_amazon, l_amazon = calcular_canal("Amazon", preco_venda, 0.15, frete_fixo=23)
m_magalu, ct_magalu, l_magalu = calcular_canal("Magalu", preco_venda, 0.15, frete_fixo=8)

comissao_ml = 0.12 if tipo_ml == "Classico" else 0.17
taxa_ml = 6.75 if preco_venda < 79 else 0
m_ml, ct_ml, l_ml = calcular_canal("ML", preco_venda, comissao_ml, frete_fixo=23, taxa_extra=taxa_ml)

# Shopee
if preco_venda <= 79.99:
    com_shopee = 0.20
    taxa_shopee = 4
elif preco_venda <= 99.99:
    com_shopee = 0.14
    taxa_shopee = 16
elif preco_venda <= 199.99:
    com_shopee = 0.14
    taxa_shopee = 20
else:
    com_shopee = 0.14
    taxa_shopee = 26

m_shopee, ct_shopee, l_shopee = calcular_canal("Shopee", preco_venda, com_shopee, taxa_extra=taxa_shopee)

# ==============================
# LAYOUT ALINHADO
# ==============================

cols = st.columns(5)

with cols[0]:
    card("🏪 Site FABI", m_site)

with cols[1]:
    card("Amazon", m_amazon)

with cols[2]:
    card("Magalu", m_magalu)

with cols[3]:
    card("Mercado Livre", m_ml)

with cols[4]:
    card("Shopee", m_shopee)

# ==============================
# MEMÓRIA DE CÁLCULO
# ==============================

with st.expander("📋 Ver Memória de Cálculo"):

    memoria = pd.DataFrame({
        "Canal": ["Site FABI", "Amazon", "Magalu", "Mercado Livre", "Shopee"],
        "Preço Venda": [preco_venda]*5,
        "Custo Total": [ct_site, ct_amazon, ct_magalu, ct_ml, ct_shopee],
        "Lucro": [l_site, l_amazon, l_magalu, l_ml, l_shopee],
        "Margem (%)": [m_site, m_amazon, m_magalu, m_ml, m_shopee]
    })

    st.dataframe(memoria, use_container_width=True)
