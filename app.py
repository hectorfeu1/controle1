import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data
def carregar_produtos():
    try:
        df = pd.read_csv(
            "dados.txt",
            sep=r"\s{2,}",   # separa por 2 ou mais espaços
            engine="python"
        )

        # Renomear colunas para padrão do sistema
        df = df.rename(columns={
            "Material": "sku",
            "DescricaoCompleta": "nome",
            "SubGrupo": "marca",
            "quantidade": "estoque",
            "custoMedio": "custo_produto"
        })

        return df.to_dict(orient="records")

    except Exception as e:
        st.error(f"Erro ao carregar dados.txt: {e}")
        return []

produtos = carregar_produtos()

if not produtos:
    st.warning("Nenhum produto carregado.")
    st.stop()

st.set_page_config(layout="wide")

# =========================
# CONFIGURAÇÕES
# =========================
IMPOSTOS_TOTAL = 0.12
ARMAZENAGEM = 0.02
fixo_rateado = 2
custos_operacionais_pedido = 3

# =========================
# BASE DE PRODUTOS
# =========================
produtos = [
    {
        "sku": "CR300",
        "nome": "Creatina 300g",
        "marca": "Growth",
        "estoque": 42,
        "custo_produto": 45
    },
    {
        "sku": "WH900",
        "nome": "Whey Protein 900g",
        "marca": "Integral",
        "estoque": 18,
        "custo_produto": 72
    }
]

marketplaces = {
    "Mercado Livre": {"comissao": 0.16, "frete": 23},
    "Shopee": {"comissao": 0.14, "frete": 0},
    "Amazon": {"comissao": 0.15, "frete": 23}
}

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
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.card-green { border-left: 6px solid #16a34a; }
.card-yellow { border-left: 6px solid #facc15; }
.card-red { border-left: 6px solid #dc2626; }

.kpi-title {
    font-size: 14px;
    opacity: 0.7;
}

.kpi-value {
    font-size: 22px;
    font-weight: bold;
}

.kpi-sub {
    font-size: 13px;
    opacity: 0.6;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.title("📊 Simulador Inteligente de Margem")

# =========================
# FILTROS DE BUSCA
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    busca_sku = st.text_input("🔎 Procurar SKU")

with col2:
    busca_nome = st.text_input("🔎 Procurar Nome")

with col3:
    preco_simulado = st.number_input("💰 Preço de Venda Simulado", value=100.0)

with col4:
    percentual_simulado = st.number_input("% Venda Simulado (desconto)", value=0.0)

margem_desejada = st.number_input("🎯 Margem Desejada (%)", value=5.0)

# =========================
# FILTRAGEM
# =========================
produtos_filtrados = []

for p in produtos:
    if busca_sku and busca_sku.lower() not in p["sku"].lower():
        continue
    if busca_nome and busca_nome.lower() not in p["nome"].lower():
        continue
    produtos_filtrados.append(p)

# =========================
# LOOP PRODUTOS
# =========================
for produto in produtos_filtrados:

    st.markdown("---")
    st.subheader(f"{produto['nome']} ({produto['sku']})")
    st.caption(f"Marca: {produto['marca']} | Estoque: {produto['estoque']} unidades")

    cols = st.columns(len(marketplaces))

    for i, (nome, dados) in enumerate(marketplaces.items()):

        with cols[i]:

            # Aplicar desconto simulado
            preco_venda = preco_simulado * (1 - percentual_simulado / 100)

            taxa_extra = 0

            # =========================
            # REGRAS MARKETPLACE
            # =========================

            if nome == "Mercado Livre":
                tipo_anuncio = st.selectbox(
                    f"Tipo ML - {produto['sku']}",
                    ["C - Classico", "P - Premium"],
                    key=f"{produto['sku']}_ml"
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
            margem = (lucro / preco_venda) * 100 if preco_venda > 0 else 0

            # =========================
            # COR DA BORDA
            # =========================
            if margem > 5:
                classe = "card-green"
            elif margem > 0:
                classe = "card-yellow"
            else:
                classe = "card-red"

            # =========================
            # CARD
            # =========================
            st.markdown(f"""
            <div class="card {classe}">
                <div class="kpi-title">{nome}</div>
                <div class="kpi-value">{margem:.2f}%</div>
                <div class="kpi-sub">Lucro: R$ {lucro:.2f}</div>
                <div class="kpi-sub">Preço Final: R$ {preco_venda:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # =========================
            # CÁLCULO EXPANDÍVEL
            # =========================
            with st.expander("Ver cálculo detalhado"):
                st.write(f"""
                **Preço Base:** R$ {preco_simulado:.2f}  
                **Desconto Aplicado:** {percentual_simulado:.2f}%  
                **Preço Final:** R$ {preco_venda:.2f}  
                **Custo Produto:** R$ {produto['custo_produto']:.2f}  
                **Comissão:** R$ {comissao:.2f}  
                **Frete:** R$ {frete:.2f}  
                **Impostos:** R$ {impostos:.2f}  
                **Armazenagem:** R$ {armazenagem:.2f}  
                **Taxa Extra:** R$ {taxa_extra:.2f}  
                **Custos Fixos:** R$ {fixo_rateado + custos_operacionais_pedido:.2f}  
                ---
                **Custo Total:** R$ {custo_total:.2f}  
                **Lucro Final:** R$ {lucro:.2f}  
                """)

if not produtos_filtrados:
    st.warning("Nenhum produto encontrado.")

