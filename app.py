import streamlit as st
import numpy as np
from scipy.stats import poisson

def safe_convert(value):
    """Converte valores de forma segura (incluindo porcentagens)"""
    try:
        if '%' in value:
            return float(value.replace('%', '')) / 100
        return float(value)
    except:
        return None

def processar_arquivo(arquivo):
    """Processa o arquivo de estatísticas e retorna um dicionário"""
    dados = {}
    for linha in arquivo:
        try:
            linha_decodificada = linha.decode("utf-8", errors='ignore').strip()
            if ":" in linha_decodificada and "===" not in linha_decodificada:
                chave, valores = linha_decodificada.split(":", 1)
                chave = chave.strip()
                
                for parte in valores.split("|"):
                    parte = parte.strip()
                    if "Time A" in parte:
                        valor = safe_convert(parte.replace("Time A", "").strip())
                        if valor is not None:
                            dados[f"{chave}_Time A"] = valor
                    elif "Time B" in parte:
                        valor = safe_convert(parte.replace("Time B", "").strip())
                        if valor is not None:
                            dados[f"{chave}_Time B"] = valor
        except Exception as e:
            st.warning(f"Ignorando linha inválida: {linha}")
    return dados

def calcular_probabilidades(lambda_poisson):
    """Calcula probabilidades usando Distribuição de Poisson"""
    return {
        k: poisson.pmf(k, lambda_poisson) * 100
        for k in range(0, 4)  # 0, 1, 2 ou 3 gols
    }

def main():
    st.title("⚽ Analisador de Probabilidades de Gols")
    st.markdown("""
    **Como usar**:
    1. Insira o placar atual
    2. Faça upload do arquivo de estatísticas
    3. Veja as probabilidades ajustadas para os últimos 10 minutos
    """)

    # Inputs do usuário
    col1, col2 = st.columns(2)
    with col1:
        placar = st.text_input("Placar atual (ex: 2 x 1)", "0 x 0")
    with col2:
        arquivo = st.file_uploader("Arquivo de estatísticas (.txt)", type="txt")

    if arquivo:
        dados = processar_arquivo(arquivo)
        
        # Processa o placar
        try:
            gols_time_a, gols_time_b = map(int, placar.split("x"))
            situacao = {
                "Time A": "ganhando" if gols_time_a > gols_time_b else 
                         "perdendo" if gols_time_a < gols_time_b else "empatando",
                "Time B": "ganhando" if gols_time_b > gols_time_a else 
                         "perdendo" if gols_time_b < gols_time_a else "empatando"
            }
        except:
            st.error("❌ Formato de placar inválido! Use '2 x 1'")
            return

        # Verifica dados mínimos necessários
        if not all(k in dados for k in ["Finalizações no alvo_Time A", "Finalizações no alvo_Time B"]):
            st.error("⚠ Arquivo incompleto. Certifique-se de incluir 'Finalizações no alvo' para ambos os times.")
            return

        # Fatores de ajuste baseados no placar
        FATORES = {
            "ganhando": 0.7,  # Reduz probabilidade
            "perdendo": 1.5,   # Aumenta probabilidade
            "empatando": 1.1    # Pequeno aumento
        }

        # Cálculo das médias ajustadas
        media_base_time_a = dados["Finalizações no alvo_Time A"] / 80  # Média por minuto
        media_base_time_b = dados["Finalizações no alvo_Time B"] / 80
        
        media_ajustada_a = media_base_time_a * FATORES[situacao["Time A"]]
        media_ajustada_b = media_base_time_b * FATORES[situacao["Time B"]]
        
        media_total = (media_ajustada_a + media_ajustada_b) * 10  # Últimos 10 minutos
        probabilidades = calcular_probabilidades(media_total)

        # Exibição dos resultados
        st.subheader(f"📊 Probabilidades (Placar: {placar})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("0 gol(s)", f"{probabilidades[0]:.1f}%")
            st.metric("2 gol(s)", f"{probabilidades[2]:.1f}%")
        with col2:
            st.metric("1 gol(s)", f"{probabilidades[1]:.1f}%")
            st.metric("3 gol(s)", f"{probabilidades[3]:.1f}%")

        # Gráfico
        st.bar_chart(probabilidades)

        # Análise contextual
        st.subheader("🔍 Interpretação")
        st.write(f"""
        **Situação atual**:
        - ⚽ Time A ({gols_time_a} gols): **{situacao['Time A'].upper()}** (fator: {FATORES[situacao['Time A']}x)
        - ⚽ Time B ({gols_time_b} gols): **{situacao['Time B'].upper()}** (fator: {FATORES[situacao['Time B']}x)

        **Estatísticas-chave**:
        - 🎯 Finalizações no alvo: Time A ({dados['Finalizações no alvo_Time A']}) | Time B ({dados['Finalizações no alvo_Time B']})
        - 🕒 Média ajustada de gols/10min: **{media_total:.2f}**
        """)

if __name__ == "__main__":
    main()
