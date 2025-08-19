import streamlit as st
import numpy as np
from scipy.stats import poisson
from streamlit.components.v1 import html

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

def copiar_texto():
    """Função JavaScript para copiar texto"""
    return """
    <script>
    function copiarTexto() {
        const texto = document.getElementById("texto-modelo").innerText;
        navigator.clipboard.writeText(texto);
        const botao = document.getElementById("botao-copiar");
        botao.innerText = "Copiado!";
        setTimeout(() => { botao.innerText = "Copiar"; }, 2000);
    }
    </script>
    """

def main():
    st.title("⚽ Analisador de Probabilidades de Gols")
    st.markdown("""
    **Como usar**:
    1. Insira o placar atual (ex: 2 x 1)
    2. Faça upload do arquivo de estatísticas (.txt)
    3. Veja as probabilidades ajustadas para os últimos 10 minutos
    """)

    # Adicionando o componente de texto copiável
    st.markdown("""
    <style>
    .caixa-texto {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 10px;
        background-color: #f9f9f9;
        margin-bottom: 10px;
        font-size: 14px;
        position: relative;
    }
    .botao-copiar {
        position: absolute;
        right: 10px;
        top: 10px;
        background-color: #f0f2f6;
        border: 1px solid #ccc;
        border-radius: 3px;
        padding: 2px 8px;
        font-size: 12px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    modelo_texto = """Quero que você extraia as estatísticas deste print e organize em um arquivo de texto no seguinte formato:

=== SEÇÃO ===
Nome da métrica: Time A valor | Time B valor

Organize por categorias (Destaques, Finalizações, Ataque, Passes, Defesa, Goleiro).
Sempre escreva os números dos dois times lado a lado, no modelo:
Métrica: Time A X | Time B Y
Se houver porcentagens ou frações (ex.: 63/81), mantenha-as.

O resultado final deve ser um TXT limpo e bem formatado, sem ruídos do OCR, apenas com os dados relevantes da imagem."""

    st.markdown("""
    <div class="caixa-texto">
        <div id="texto-modelo">Quero que você extraia as estatísticas deste print e organize em um arquivo de texto no seguinte formato:

=== SEÇÃO ===
Nome da métrica: Time A valor | Time B valor

Organize por categorias (Destaques, Finalizações, Ataque, Passes, Defesa, Goleiro).
Sempre escreva os números dos dois times lado a lado, no modelo:
Métrica: Time A X | Time B Y
Se houver porcentagens ou frações (ex.: 63/81), mantenha-as.

O resultado final deve ser um TXT limpo e bem formatado, sem ruídos do OCR, apenas com os dados relevantes da imagem.</div>
        <button id="botao-copiar" class="botao-copiar" onclick="copiarTexto()">Copiar</button>
    </div>
    """, unsafe_allow_html=True)

    html(copiar_texto())

    # Restante do código (inputs, processamento, etc.)
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

        if not all(k in dados for k in ["Finalizações no alvo_Time A", "Finalizações no alvo_Time B"]):
            st.error("⚠ Arquivo incompleto. Certifique-se de incluir 'Finalizações no alvo' para ambos os times.")
            return

        FATORES = {
            "ganhando": 0.7,
            "perdendo": 1.5,
            "empatando": 1.1
        }

        media_base_time_a = dados["Finalizações no alvo_Time A"] / 80
        media_base_time_b = dados["Finalizações no alvo_Time B"] / 80
        
        media_ajustada_a = media_base_time_a * FATORES[situacao["Time A"]]
        media_ajustada_b = media_base_time_b * FATORES[situacao["Time B"]]
        
        media_total = (media_ajustada_a + media_ajustada_b) * 10
        probabilidades = calcular_probabilidades(media_total)

        st.subheader(f"📊 Probabilidades (Placar: {placar})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("0 gol(s)", f"{probabilidades[0]:.1f}%")
            st.metric("2 gol(s)", f"{probabilidades[2]:.1f}%")
        with col2:
            st.metric("1 gol(s)", f"{probabilidades[1]:.1f}%")
            st.metric("3 gol(s)", f"{probabilidades[3]:.1f}%")

        st.bar_chart(probabilidades)

        st.subheader("🔍 Interpretação")
        st.write(f"""
        **Situação atual**:
        - ⚽ Time A ({gols_time_a} gols): **{situacao['Time A'].upper()}** (fator: {FATORES[situacao['Time A']]}x)
        - ⚽ Time B ({gols_time_b} gols): **{situacao['Time B'].upper()}** (fator: {FATORES[situacao['Time B']]}x)

        **Estatísticas-chave**:
        - 🎯 Finalizações no alvo: Time A ({dados['Finalizações no alvo_Time A']}) | Time B ({dados['Finalizações no alvo_Time B']})
        - 🕒 Média ajustada de gols/10min: **{media_total:.2f}**
        """)

# ... (código existente que calcula as probabilidades)

# ====== ADICIONE AQUI O NOVO CÓDIGO ======
filtros = calcular_filtros_seguranca(dados, placar)

# Exiba os filtros na seção "Interpretação"
st.subheader("🔍 Interpretação")
st.write(f"""
**Situação atual**:
- ⚽ Time A ({gols_time_a} gols): **{situacao['Time A'].upper()}** (fator: {FATORES[situacao['Time A']]}x)
- ⚽ Time B ({gols_time_b} gols): **{situacao['Time B'].upper()}** (fator: {FATORES[situacao['Time B']]}x)

**Estatísticas-chave**:
- 🎯 Finalizações no alvo: Time A ({dados['Finalizações no alvo_Time A']}) | Time B ({dados['Finalizações no alvo_Time B']})
- 🕒 Média ajustada de gols/10min: **{media_total:.2f}**

**Filtros de Segurança** (para Under):
- 🔒 Time perdedor com pouca pressão (<2 chutes no alvo): {"✅" if filtros["pressao_perdedor"] else "❌"}
- ⏱️ Jogo interrompido (>20 faltas): {"✅" if filtros["tempo_efetivo"] else "❌"}
- 🎯 Poucas chances claras (<2 no total): {"✅" if filtros["chances_claras"] else "❌"}
""")
# ====== FIM DO CÓDIGO NOVO ======

if __name__ == "__main__":
    main()
