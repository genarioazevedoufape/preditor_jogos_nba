import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
from datetime import datetime

def convert_height_inches_to_meters(height_inches):
    return round(height_inches * 0.0254, 2)

def convert_weight_pounds_to_kg(weight_pounds):
    return round(weight_pounds * 0.453592, 1)

def format_salary(salary):
    return f'${salary:,.2f}'

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

def get_game_log(player_id, season='2024-25'):
    """Obtém o log de jogos do jogador para a temporada especificada."""
    log = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    log = log.rename(columns={
        "GAME_DATE": "Data do Jogo",
        "MATCHUP": "Adversário",
        "WL": "Vitória/Derrota",
        "PTS": "Pontos",
        "REB": "Rebotes",
        "AST": "Assistências",
        "FG3A": "Tentativas de 3PTS",
        "FG3M": "Cestas de 3PTS",
        "MIN": "Minutos em Quadra"
    })
    log["Casa/Fora"] = log["Adversário"].apply(lambda x: "Casa" if "vs." in x else "Fora")
    log["Adversário"] = log["Adversário"].str.split().str[-1]
    return log

# Configuração da página
st.set_page_config(page_title="Charlotte Hornets Dashboard", layout="wide")
st.title("\U0001F3C0 Charlotte Hornets - Análise de Dados")

# Seleção de jogador dentro da aba
player_ids = {"LaMelo Ball": 1630163, "Brandon Miller": 1641706, "Moussa Diabate": 1631217}
st.subheader("\U0001F4CC Selecione um jogador para análise")
player_name = st.selectbox("Escolha um jogador", list(player_ids.keys()))
player_id = player_ids[player_name]

dados_jogador = get_player_data(player_id)
st.subheader(f"\U0001F4CC Informações de {player_name}")
st.table(pd.DataFrame([dados_jogador]))

df_jogos = get_game_log(player_id)
st.subheader("\U0001F4CA Estatísticas da Temporada Atual")
st.dataframe(df_jogos)

# Gráficos interativos
fig_pts = px.line(df_jogos, x="Data do Jogo", y="Pontos", title="Pontos por Jogo", markers=True)
st.plotly_chart(fig_pts, use_container_width=True)

# Definir as colunas específicas para o confronto
colunas_especificas = ["Data do Jogo", "Casa/Fora", "Vitória/Derrota", "Pontos", "Rebotes", "Assistências", "Tentativas de 3PTS", "Cestas de 3PTS", "Minutos em Quadra"]

# Escolher um adversário para análise específica
st.subheader("\U0001F4CC Selecione um adversário para análise detalhada")
adversario_selecionado = st.selectbox("Escolha um adversário", df_jogos["Adversário"].unique())

# Filtrar os jogos contra o adversário escolhido e selecionar apenas as colunas desejadas
df_partida = df_jogos[df_jogos["Adversário"] == adversario_selecionado][colunas_especificas]

st.subheader(f"\U0001F4CC Jogos contra {adversario_selecionado}")
st.dataframe(df_partida)
