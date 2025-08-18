
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Estatísticas de Futebol", layout="centered")

st.title("📊 Análise de Estatísticas de Futebol")

# Input de placar
st.subheader("⚽ Placar do Jogo")
time_a_score = st.number_input("Gols do Time A", min_value=0, step=1)
time_b_score = st.number_input("Gols do Time B", min_value=0, step=1)

# Upload do JSON
st.subheader("📁 Carregar Arquivo JSON de Estatísticas")
uploaded_file = st.file_uploader("Faça upload do arquivo .json", type="json")

if uploaded_file:
    try:
        df = pd.read_json(uploaded_file)

        # Validação
        if not all(col in df.columns for col in ["Estatística", "Time A", "Time B"]):
            st.error("O arquivo JSON precisa conter as colunas: 'Estatística', 'Time A' e 'Time B'")
        else:
            st.success("Arquivo carregado com sucesso!")

            # Calcular domínio de cada estatística
            df["Domínio do Time A (%)"] = round((df["Time A"] / (df["Time A"] + df["Time B"])) * 100, 1)
            df["Domínio do Time B (%)"] = round((df["Time B"] / (df["Time A"] + df["Time B"])) * 100, 1)

            # Mostrar placar e estatísticas
            st.markdown(f"### 📌 Placar: **Time A {int(time_a_score)} x {int(time_b_score)} Time B**")

            st.subheader("📊 Estatísticas Detalhadas")
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo JSON: {e}")
