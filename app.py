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
        st.write("Estatísticas processadas:", dados)
        
        # Verifica se há dados suficientes
        if "Finalizações no alvo_Time A" in dados and "Finalizações no alvo_Time B" in dados:
            total_chutes_alvo = dados["Finalizações no alvo_Time A"] + dados["Finalizações no alvo_Time B"]
            media_gols_por_minuto = total_chutes_alvo / 80  # Supondo 80 minutos de jogo
            probabilidades = calcular_probabilidades(media_gols_por_minuto * 10)  # Últimos 10 minutos
            
            # Exibe resultados
            st.subheader("Probabilidades nos últimos 10 minutos")
            for gols, prob in probabilidades.items():
                st.write(f"{gols} gol(s): {prob:.1f}%")
            
            # Análise contextual
            st.subheader("Interpretação")
            posse_time_a = dados.get("Posse de bola_Time A", 0)
            posse_time_b = dados.get("Posse de bola_Time B", 0)
            st.write(f"""
                - **Posse de bola**: Time A ({posse_time_a}%) vs Time B ({posse_time_b}%).
                - **Chutes no alvo**: {total_chutes_alvo} (Time A: {dados["Finalizações no alvo_Time A"]} | Time B: {dados["Finalizações no alvo_Time B"]}).
                - **Probabilidade mais alta**: {max(probabilidades.values()):.1f}% para {max(probabilidades, key=probabilidades.get)} gol(s).
            """)
        else:
            st.error("Dados insuficientes para cálculo. Verifique o arquivo.")

def processar_arquivo(arquivo):
    dados = {}
    for linha in arquivo:
        try:
            linha_decodificada = linha.decode("utf-8").strip()
            if ":" in linha_decodificada and "===" not in linha_decodificada:
                chave, valores = linha_decodificada.split(":", 1)
                chave = chave.strip()
                partes = [v.strip() for v in valores.split("|")]
                
                for parte in partes:
                    if "Time A" in parte or "Time B" in parte:
                        time = "Time A" if "Time A" in parte else "Time B"
                        valor_texto = parte.replace(time, "").strip()
                        
                        # Tratamento robusto do valor
                        if valor_texto:  # Verifica se não está vazio
                            # Remove % se existir
                            if "%" in valor_texto:
                                valor_texto = valor_texto.replace("%", "")
                                try:
                                    valor = float(valor_texto) / 100
                                except ValueError:
                                    continue  # Pula valores inválidos
                            else:
                                try:
                                    valor = float(valor_texto)
                                except ValueError:
                                    continue  # Pula valores inválidos
                            
                            dados[f"{chave}_{time}"] = valor
        except Exception as e:
            st.warning(f"Ignorando linha inválida: {linha}. Erro: {str(e)}")
            continue
            
    return dados
Principais Melhoria

def calcular_probabilidades(lambda_poisson):
    return {
        k: poisson.pmf(k, lambda_poisson) * 100
        for k in range(0, 4)  # Probabilidade para 0, 1, 2 ou 3 gols
    }

if __name__ == "__main__":
    main()
