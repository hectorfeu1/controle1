import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# CONFIGURAÇÕES
# =========================
IMPOSTOS_TOTAL = 0.12
ARMAZENAGEM = 0.02
fixo_rateado = 2
custos_operacionais_pedido = 3

# =========================
# CARREGAMENTO ULTRA OTIMIZADO
# =========================
@st.cache_data(show_spinner=False)
def carregar_produtos():
    df = pd.read_csv(
        "dados.txt",
        sep="\t",
        encoding="utf-8",
        dtype={
            "Material": str,
            "DescricaoCompleta": str,
            "SubGrupo": str
        }
    )

    df = df.rename(columns={
        "Material": "sku",
        "DescricaoCompleta": "nome",
        "SubGrupo": "marca",
        "quantidade": "estoque",
        "custoMedio": "custo_produto"
    })

    df["custo_produto"] = pd.to_numeric(df["custo_produto"], errors="coerce")
    df["estoque"] = pd.to_numeric(df["estoque"], errors="coerce")

    return df

df_produtos = carregar_produtos()

# =========================
# CSS DASHBOARD
# =========================
st.markdown("""
<style>

.card {
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
    background-color: var(--background-color);
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.card-green { border-left: 6px solid #16a34a; }
.card-yellow { border-left: 6px solid #facc15; }
.card-red { border-left: 6px solid #dc2626; }

.kpi-title { font-size: 14px; opacity: 0.7; }
.kpi-value { font-size: 22px; font-weight: bold; }
.kpi-sub { font-size: 13px; opacity: 0.6; }

</style>
""", unsafe_allow_html=True)

# =========================
# MARKETPLACES
# =========================
marketplaces = {
    "Mercado Livre": {"comissao": 0.16, "frete": 23},
    "Shopee": {"comissao": 0.14, "frete": 0},
    "Amazon": {"comissao": 0.15, "frete": 23}
}

# =========================
# TÍTULO
# =========================
st.title("📊 Simulador Inteligente de Margem")

# =========================
# BUSCA (OBRIGATÓRIA)
# =========================
col1, col2 = st.columns(2)

with col1:
    busca_sku = st.text_input("🔎 Procurar SKU")

with col2:
    busca_nome = st.text_input("🔎 Procurar Nome")

if not busca_sku and not busca_nome:
    st.info("Digite um SKU ou Nome para iniciar a busca.")
    st.stop()

# =========================
# FILTRO OTIMIZADO
# =========================
filtro = df_produtos

if busca_sku:
    filtro = filtro[filtro["sku"].str.contains(busca_sku, case=False, na=False)]

if busca_nome:
    filtro = filtro[filtro["nome"].str.contains(busca_nome, case=False, na=False)]

filtro = filtro.head(1)

if filtro.empty:
    st.warning("Produto não encontrado.")
    st.stop()

produto = filtro.iloc[0]

# =========================
# DADOS PRODUTO
# =========================
st.markdown("---")
st.subheader(f"{produto['nome']} ({produto['sku']})")
st.caption(f"Marca: {produto['marca']} | Estoque: {int(produto['estoque'])} unidades")

# =========================
# SIMULAÇÃO
# =========================
colA, colB, colC = st.columns(3)

with colA:
    preco_simulado = st.number_input("💰 Preço de Venda Simulado", value=100.0)

with colB:
    percentual_simulado = st.number_input("% Venda Simulado (desconto)", value=0.0)

with colC:
    margem_desejada = st.number_input("🎯 Margem Desejada (%)", value=5.0)

preco_venda = preco_simulado * (1 - percentual_simulado / 100)

# =========================
# CARDS MARKETPLACES
# =========================
cols = st.columns(len(marketplaces))

for i, (nome, dados) in enumerate(marketplaces.items()):

    with cols[i]:

        taxa_extra = 0

        if nome == "Mercado Livre":
            tipo_anuncio = st.selectbox(
                "Tipo ML",
                ["C - Classico", "P - Premium"],
                key="ml_tipo"
            )
            comissao = preco_venda * (0.12 if tipo_anuncio.startswith("C") else 0.17)
            if preco_venda < 79:
                taxa_extra = 6.75
            frete = 23

        elif nome == "Shopee":
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

        elif nome == "Amazon":
            comissao = preco_venda * dados["comissao"]
            frete = 23

        impostos = preco_venda * IMPOSTOS_TOTAL
        armazenagem = preco_venda * ARMAZENAGEM

        custo_total = (
            float(produto["custo_produto"])
            + comissao
            + frete
            + impostos
            + armazenagem
            + fixo_rateado
            + custos_operacionais_pedido
            + taxa_extra
        )

        lucro = preco_venda - custo_total
        margem = (lucro / preco_venda) * 100 if preco_venda > 0 else 0

        if margem > 5:
            classe = "card-green"
        elif margem > 0:
            classe = "card-yellow"
        else:
            classe = "card-red"

        st.markdown(f"""
        <div class="card {classe}">
            <div class="kpi-title">{nome}</div>
            <div class="kpi-value">{margem:.2f}%</div>
            <div class="kpi-sub">Lucro: R$ {lucro:.2f}</div>
            <div class="kpi-sub">Preço Final: R$ {preco_venda:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Ver cálculo detalhado"):
            st.write(f"""
            **Preço Base:** R$ {preco_simulado:.2f}  
            **Desconto:** {percentual_simulado:.2f}%  
            **Preço Final:** R$ {preco_venda:.2f}  
            **Custo Produto:** R$ {float(produto['custo_produto']):.2f}  
            **Comissão:** R$ {comissao:.2f}  
            **Frete:** R$ {frete:.2f}  
            **Impostos:** R$ {impostos:.2f}  
            **Armazenagem:** R$ {armazenagem:.2f}  
            **Taxa Extra:** R$ {taxa_extra:.2f}  
            **Custo Total:** R$ {custo_total:.2f}  
            **Lucro Final:** R$ {lucro:.2f}  
            """)
