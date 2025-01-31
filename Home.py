import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leaguegamefinder


# Configuração da página
st.set_page_config(
    page_title="Charlotte Hornets",
    page_icon="img/Charlotte_Hornets.png",  # Certifique-se de que o caminho da imagem está correto
    layout="wide",
)

# Layout do título com logo
col1, col2 = st.columns([1, 8])
with col1:
    st.image("img/Charlotte_Hornets.png", width=100)  # Certifique-se de que o caminho da imagem está correto
with col2:
    st.title("Charlotte Hornets")

# Expander com informações sobre o time
with st.expander("Saiba mais"):
    st.write('''O Charlotte Hornets é um time norte-americano de basquete profissional com sede em Charlotte, Carolina do Norte. 
             Os Hornets competem na National Basketball Association (NBA) como um membro da Divisão Sudeste da Conferência Leste.''')

# Título da seção de estatísticas
st.write('## Estatísticas da Temporada 2020-2021')

# Exemplo de DataFrame para a tabela de classificação
data = {
    "Posição": [1, 2, 3, 4, 5],
    "Time": ["Philadelphia 76ers", "Brooklyn Nets", "Milwaukee Bucks", "New York Knicks", "Atlanta Hawks"],
    "Vitórias": [49, 48, 46, 41, 41],
    "Derrotas": [23, 24, 26, 31, 31],
    "Percentual de Vitórias": [0.681, 0.667, 0.639, 0.569, 0.569],
}

df = pd.DataFrame(data)

# Exibir a tabela de classificação
st.write('### Tabela de Classificação')
st.dataframe(df)

# Gráfico interativo com Plotly
st.write('### Gráfico de Percentual de Vitórias')
fig = px.bar(df, x="Time", y="Percentual de Vitórias", title="Percentual de Vitórias por Time", color="Time")
st.plotly_chart(fig, use_container_width=True)

# Adicionar mais estatísticas ou gráficos conforme necessário
st.write('### Outras Estatísticas')
st.write('Aqui você pode adicionar mais gráficos ou tabelas com estatísticas detalhadas do Charlotte Hornets.')

