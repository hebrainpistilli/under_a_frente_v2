import streamlit as st
import numpy as np
from scipy.stats import poisson

def safe_convert(value):
    try:
        if '%' in value:
            return float(value.replace('%', '')) / 100
        return float(value)
    except:
        return None

def processar_arquivo(arquivo):
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
    return {
        k: poisson.pmf(k, lambda_poisson) * 100
        for k in range(0, 4)
    }

def main():
    st.title("Análise Estatística de Jogos ⚽")
    
    placar = st.text_input("Placar atual (ex: 2 x 1)", "0 x 0")
    arquivo = st.file_uploader("Upload do arquivo de estatísticas (.txt)", type="txt")
    
    if arquivo:
        dados = processar_arquivo(arquivo)
        st.write("Estatísticas processadas:", dados)
        
        if "Finalizações no alvo_Time A" in dados and "Finalizações no alvo_Time B" in dados:
            total_chutes_alvo = dados["Finalizações no alvo_Time A"] + dados["Finalizações no alvo_Time B"]
            media_gols_por_minuto = total_chutes_alvo / 80
            probabilidades = calcular_probabilidades(media_gols_por_minuto * 10)
            
            st.subheader("Probabilidades nos últimos 10 minutos")
            for gols, prob in probabilidades.items():
                st.write(f"{gols} gol(s): {prob:.1f}%")
            
            st.subheader("Interpretação")
            st.write(f"""
                - Posse de bola: Time A ({dados.get('Posse de bola_Time A', 0)*100:.0f}%) vs Time B ({dados.get('Posse de bola_Time B', 0)*100:.0f}%)
                - Chutes no alvo: {total_chutes_alvo}
                - Probabilidade mais alta: {max(probabilidades.values()):.1f}% para {max(probabilidades, key=probabilidades.get)} gol(s)
            """)

if __name__ == "__main__":
    main()
