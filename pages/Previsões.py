import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
from scipy.stats import gumbel_r
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams

# Encontrar o ID do Charlotte Hornets
hornets = teams.find_team_by_abbreviation('CHA')
hornets_id = hornets['id']

# Extrair os dados dos jogos para as temporadas 23-24 e 24-25
game_logs_23_24 = teamgamelog.TeamGameLog(team_id=hornets_id, season='2023-24').get_data_frames()[0]
game_logs_24_25 = teamgamelog.TeamGameLog(team_id=hornets_id, season='2024-25').get_data_frames()[0]

# Combinar os dados das duas temporadas
all_game_logs = pd.concat([game_logs_23_24, game_logs_24_25])

# Função para aplicar o Método de Gumbel
def aplicar_gumbel(dados, coluna, X):
    params = gumbel_r.fit(dados[coluna])
    mu, beta = params

    resultados = {
        "Probabilidade de marcar acima de X": 1 - gumbel_r.cdf(X, loc=mu, scale=beta),
        "Probabilidade de atingir ou exceder X": 1 - gumbel_r.cdf(X, loc=mu, scale=beta),
        "Probabilidade de atingir ou ficar abaixo de X": gumbel_r.cdf(X, loc=mu, scale=beta),
        "Proporção de valores menores ou iguais a X": gumbel_r.cdf(X, loc=mu, scale=beta),
        "Valores menores que X": np.sum(dados[coluna] < X),
        "Proporção de valores menores que X": np.mean(dados[coluna] < X)
    }
    return resultados, mu, beta

# Interface Streamlit
st.title("Análise de Eventos Extremos na NBA - Charlotte Hornets")
st.write("Modelo baseado na Distribuição de Gumbel para prever pontuação, assistências e rebotes extremos.")

# Seleção do usuário
estatistica = st.selectbox("Selecione a estatística:", ["PTS", "AST", "REB"])
X = st.number_input("Defina o valor de X:", min_value=0, value=100)

# Aplicar Gumbel
resultados, mu, beta = aplicar_gumbel(all_game_logs, estatistica, X)

# Exibir resultados
st.subheader(f"Resultados para {estatistica} com X = {X}")
for pergunta, resposta in resultados.items():
    st.write(f"**{pergunta}:** {resposta:.4f}")

# Gráfico da Distribuição de Gumbel
x = np.linspace(min(all_game_logs[estatistica]), max(all_game_logs[estatistica]), 1000)
y = gumbel_r.pdf(x, loc=mu, scale=beta)

# Criar histograma dos dados
hist_data = [all_game_logs[estatistica]]
group_labels = [estatistica]

# Criar figura com histograma e curva de Gumbel
fig = ff.create_distplot(hist_data, group_labels, show_hist=True, show_curve=False)
fig.add_scatter(x=x, y=y, mode='lines', name=f"Gumbel (μ={mu:.2f}, β={beta:.2f})")
fig.add_vline(x=X, line=dict(color="red", dash="dash"), annotation_text=f"X = {X}")

st.plotly_chart(fig)