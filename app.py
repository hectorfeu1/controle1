import streamlit as st
import pandas as pd

PEDIDOS_MES = 10000

marketplaces = {
    "Amazon": {"comissao": 0.12},
    "Americanas": {"comissao": 0.17, "frete_percent": 0.08},
    "Magalu": {"comissao": 0.148},
    "Mercado Livre": {"comissao": 0.17},
    "Olist": {"comissao": 0.19, "frete_percent": 0.11},
    "Shopee": {"comissao": 0.14},
}

custos_fixos_mensais = 382 + 660 + 349 + 1945.38 + 17560 + 17000
custos_operacionais_pedido = 2.625

ICMS = 0.0125
DIFAL = 0.0655
PIS_COFINS = 0.0925
ARMAZENAGEM = 0.018

IMPOSTOS_TOTAL = ICMS + DIFAL + PIS_COFINS

st.set_page_config(layout="wide")

st.title("Calculadora de Margem - Fabricante Online")
st.write("Envie um arquivo com colunas: sku, nome, custo_produto")

uploaded_file = st.file_uploader("Upload arquivo", type=["csv","txt"])

if uploaded_file is not None:

    try:
        try:
            df = pd.read_csv(uploaded_file, sep="\t", encoding="latin-1")
        except:
            df = pd.read_csv(uploaded_file, sep=",", encoding="latin-1")

        df.columns = df.columns.str.strip().str.lower()

        if not all(c in df.columns for c in ["sku","nome","custo_produto"]):
            st.error("Arquivo precisa ter sku, nome, custo_produto")
            st.stop()

        df["custo_produto"] = df["custo_produto"].astype(float)

        st.success(f"{len(df)} produtos carregados")

    except Exception as e:
        st.error(e)
        st.stop()

    sku = st.text_input("Digite o SKU")

    if sku:

        prod = df[df["sku"].astype(str) == sku]

        if prod.empty:
            st.warning("SKU não encontrado")
            st.stop()

        prod = prod.iloc[0]

        st.subheader(prod["nome"])
        st.write(f"Custo: R$ {prod['custo_produto']:.2f}")

        preco = st.number_input("Preço de venda",0.01,step=0.01)

        st.subheader("Simulação de desconto")

        c1,c2,c3 = st.columns(3)

        with c1:
            desconto = st.number_input("Desconto %",0.0,90.0,0.0)

        with c2:
            desc_voce = st.number_input("% pago por você",0.0,100.0,100.0)

        with c3:
            rebate = st.number_input("% pago pelo canal",0.0,100.0,0.0)

        desconto /= 100
        desc_voce /= 100
        rebate /= 100

        tipo_ml = st.selectbox("Tipo anúncio ML",["Classico","Premium"])

        if preco > 0:

            preco_desc = preco * (1 - desconto)
            valor_desc = preco - preco_desc

            parte_voce = valor_desc * desc_voce
            parte_canal = valor_desc * rebate

            receita = preco_desc + parte_canal

            st.info(f"""
Preço original: R$ {preco:.2f}

Preço com desconto: R$ {preco_desc:.2f}

Desconto total: R$ {valor_desc:.2f}

Parte paga por você: R$ {parte_voce:.2f}

Rebate canal: R$ {parte_canal:.2f}

Receita final: R$ {receita:.2f}
""")

            fixo = custos_fixos_mensais / PEDIDOS_MES

            resultados = []

            for nome,dados in marketplaces.items():

                taxa_extra = 0
                frete_percent = 0
                comissao_percent = dados["comissao"]

                if nome == "Mercado Livre":

                    comissao_percent = 0.12 if tipo_ml=="Classico" else 0.17
                    frete = 23

                    if receita < 79:
                        taxa_extra = 6.75

                elif nome == "Shopee":

                    if receita <= 79.99:
                        comissao_percent = 0.20
                        taxa_extra = 4
                    elif receita <= 99.99:
                        comissao_percent = 0.14
                        taxa_extra = 16
                    elif receita <= 199.99:
                        comissao_percent = 0.14
                        taxa_extra = 20
                    else:
                        comissao_percent = 0.14
                        taxa_extra = 26

                    frete = 0

                elif nome == "Amazon":

                    # REGRA AJUSTADA AQUI
                    if preco_desc < 79:
                        frete = 6.50
                    else:
                        frete = 21.90

                elif nome == "Magalu":

                    frete = 12

                else:

                    frete_percent = dados.get("frete_percent",0)
                    frete = receita * frete_percent

                comissao = receita * comissao_percent

                impostos = receita * IMPOSTOS_TOTAL
                armazenagem = receita * ARMAZENAGEM

                custo_total = (
                    prod["custo_produto"] +
                    comissao +
                    frete +
                    impostos +
                    armazenagem +
                    fixo +
                    custos_operacionais_pedido +
                    taxa_extra
                )

                lucro = receita - custo_total
                margem = (lucro/receita)*100 if receita>0 else 0

                percentual_total = (
                    comissao_percent +
                    IMPOSTOS_TOTAL +
                    ARMAZENAGEM +
                    frete_percent
                )

                custo_fixo = (
                    prod["custo_produto"] +
                    frete +
                    fixo +
                    custos_operacionais_pedido +
                    taxa_extra
                )

                if percentual_total < 1:
                    preco_min = custo_fixo / (1 - percentual_total)
                else:
                    preco_min = 0

                resultados.append((nome,lucro,margem,preco_min))

            cols = st.columns(6)

            for i,r in enumerate(resultados):

                nome,lucro,margem,preco_min = r

                if margem < 2:
                    cor = "#ff4b4b"
                elif margem <=5:
                    cor = "#f0ad4e"
                else:
                    cor = "#28a745"

                with cols[i]:

                    st.markdown(f"""
<div style="
border:2px solid {cor};
padding:8px;
border-radius:8px;
text-align:center;
font-size:14px">

<b>{nome}</b><br>

Lucro<br>
<b>R$ {lucro:.2f}</b><br>

Margem<br>
<b>{margem:.1f}%</b><br>

Preço 0%<br>
<b>R$ {preco_min:.2f}</b>

</div>
""",unsafe_allow_html=True)
