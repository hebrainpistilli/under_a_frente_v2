import streamlit as st
import numpy as np
from scipy.stats import poisson

def main():
    st.title("Análise Estatística de Jogos ⚽")
    
    # Inputs
    st.subheader("Dados do Jogo")
    placar = st.text_input("Placar atual (ex: 2 x 1)", "0 x 0")
    arquivo = st.file_uploader("Upload do arquivo de estatísticas (.txt)", type="txt")
    
    if arquivo:
        dados = processar_arquivo(arquivo)
        st.write("Estatísticas carregadas:", dados)
        
        # Cálculo de probabilidades (exemplo com Poisson)
        if "chutes_no_alvo" in dados:
            media_gols_por_minuto = dados["chutes_no_alvo"] / 80  # Supondo 80 minutos de jogo
            probabilidades = calcular_probabilidades(media_gols_por_minuto * 10)  # Últimos 10 minutos
            
            # Output
            st.subheader("Probabilidades nos últimos 10 minutos")
            for gols, prob in probabilidades.items():
                st.write(f"{gols} gol(s): {prob:.1f}%")
            
            # Resumo interpretativo
            st.subheader("Análise")
            st.write(f"""
                Com {dados.get('posse_bola', 'N/A')}% de posse de bola e 
                {dados.get('chutes_no_alvo', 0)} chutes no alvo, a probabilidade de mais gols é:
                - **Alta** se acima de 50%.
                - **Média** se entre 20% e 50%.
                - **Baixa** se abaixo de 20%.
            """)

def processar_arquivo(arquivo):
    dados = {}
    for linha in arquivo:
        linha_decodificada = linha.decode("utf-8").strip()
        if ":" in linha_decodificada:
            chave, valor = linha_decodificada.split(":")
            dados[chave.strip()] = float(valor.strip())
    return dados

def calcular_probabilidades(lambda_poisson):
    return {
        k: poisson.pmf(k, lambda_poisson) * 100
        for k in range(0, 4)  # Probabilidade para 0, 1, 2 ou 3 gols
    }

if __name__ == "__main__":
    main()
