import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
from datetime import datetime

# Funções auxiliares para conversões
def convert_height_inches_to_meters(height_inches):
    return round(height_inches * 0.0254, 2)

def convert_weight_pounds_to_kg(weight_pounds):
    return round(weight_pounds * 0.453592, 1)

def get_player_data(player_id):
    """Obtém os dados básicos do jogador."""
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
    birth_date = datetime.strptime(player_info.loc[0, "BIRTHDATE"], "%Y-%m-%dT%H:%M:%S")
    today = datetime.today()
    idade = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    altura_em_polegadas = float(player_info.loc[0, "HEIGHT"].split('-')[0]) * 12 + float(player_info.loc[0, "HEIGHT"].split('-')[1])
    peso_em_libras = float(player_info.loc[0, "WEIGHT"])

    return {
        "ID": player_id,
        "Nome": player_info.loc[0, "DISPLAY_FIRST_LAST"],
        "Altura (m)": convert_height_inches_to_meters(altura_em_polegadas),
        "Peso (kg)": convert_weight_pounds_to_kg(peso_em_libras),
        "Idade": idade,
        "Experiência (anos)": player_info.loc[0, "SEASON_EXP"],
        "Posição": player_info.loc[0, "POSITION"],
        "Universidade": player_info.loc[0, "SCHOOL"],
        "Salário": "Não disponível na API"
    }

def get_game_log(player_id, season='2023-24'):
    """Obtém o log de jogos do jogador para a temporada especificada."""
    log = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    log = log.rename(columns={
        "GAME_DATE": "Data do Jogo",
        "MATCHUP": "Adversário",
        "WL": "Vitória/Derrota",
        "PTS": "Pontos",
        "REB": "Rebotes",
        "AST": "Assistências",
        "MIN": "Minutos em Quadra"
    })
    log["Casa/Fora"] = log["Adversário"].apply(lambda x: "Casa" if "vs." in x else "Fora")
    log["Adversário"] = log["Adversário"].str.split().str[-1]
    return log

# Função para calcular estatísticas
def calculate_statistics(df):
    """Calcula estatísticas relevantes a partir do DataFrame."""
    statistics = []
    for column in ["Pontos", "Rebotes", "Assistências"]:
        statistics.append({
            "Estatística": column,
            "Média": round(df[column].mean(), 2),
            "Mediana": round(df[column].median(), 2),
            "Moda": int(df[column].mode()[0]),
            "Desvio Padrão": round(df[column].std(), 2)
        })
    return pd.DataFrame(statistics)

# Configuração da página
st.set_page_config(page_title="NBA Player Analysis", layout="wide")
st.title("🏀 Análise de Jogadores da NBA")

# Seleção de jogador
player_ids = {"LaMelo Ball": 1630163, "Brandon Miller": 1641706, "Moussa Diabate": 1631217}
player_name = st.selectbox("Escolha um jogador", list(player_ids.keys()))
player_id = player_ids[player_name]

# Dados do jogador
dados_jogador = get_player_data(player_id)

# Organização em colunas para exibir dados do jogador
st.subheader(f"📌 Informações de {player_name}")
col1, col2 = st.columns(2)
with col1:
    st.table(pd.DataFrame([dados_jogador]))

# Log de jogos
df_jogos = get_game_log(player_id)
st.subheader("📊 Estatísticas da Temporada Atual")
st.dataframe(df_jogos, use_container_width=True)

# Estatísticas calculadas
st.subheader("📌 Estatísticas Calculadas")
estatisticas_df = calculate_statistics(df_jogos)
st.table(estatisticas_df)

# Gráficos
st.subheader("📊 Gráficos de Desempenho")

# Gráfico de distribuição de pontos, rebotes e assistências
for stat in ["Pontos", "Rebotes", "Assistências"]:
    fig = px.histogram(df_jogos, x=stat, nbins=10, title=f"Distribuição de {stat}")
    st.plotly_chart(fig, use_container_width=True)

# Box Plot
fig_box = go.Figure()
for stat in ["Pontos", "Rebotes", "Assistências"]:
    fig_box.add_trace(go.Box(y=df_jogos[stat], name=stat))
fig_box.update_layout(title="Box Plot - Pontos, Rebotes e Assistências")
st.plotly_chart(fig_box, use_container_width=True)

# Comparação da carreira
st.subheader("📌 Comparação com a Carreira")
df_carreira = pd.DataFrame({
    "Estatísticas": ["Total de Jogos", "Média de Pontos", "Média de Assistências", "Média de Rebotes", "Minutos em Quadra"],
    "Temporada Atual": [df_jogos.shape[0], df_jogos["Pontos"].mean(), df_jogos["Assistências"].mean(), df_jogos["Rebotes"].mean(), df_jogos["Minutos em Quadra"].mean()],
    "Carreira": [82, 20, 7, 5, 30]  # Exemplo de valores médios da carreira
})
st.table(df_carreira)
