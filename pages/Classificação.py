import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leaguegamefinder

# Definição das conferências
eastern_conference_teams = {
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DET", "IND", "MIA", "MIL",
    "NYK", "ORL", "PHI", "TOR", "WAS"
}

western_conference_teams = {
    "DAL", "DEN", "GSW", "HOU", "LAC", "LAL", "MEM", "MIN", "NOP", "OKC",
    "PHX", "POR", "SAC", "SAS", "UTA"
}

# Função para buscar jogos por temporada
def get_games_by_season(season):
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        games = gamefinder.get_data_frames()[0]
        return games
    except Exception as e:
        st.error(f"Erro ao buscar jogos da temporada {season}: {e}")
        return pd.DataFrame()

# Função para calcular a posição atual dos times
def calculate_standings(games):
    if games.empty:
        return pd.DataFrame()
    
    # Filtrar jogos já realizados
    games_played = games[games['WL'].notnull()]
    
    # Calcular vitórias e derrotas
    standings = games_played.groupby('TEAM_ABBREVIATION').agg(
        Wins=('WL', lambda x: (x == 'W').sum()),
        Losses=('WL', lambda x: (x == 'L').sum())
    )
    
    # Adicionar a taxa de vitória (Win Percentage)
    standings['Win_Percentage'] = standings['Wins'] / (standings['Wins'] + standings['Losses'])
    
    # Ordenar por taxa de vitória
    standings = standings.sort_values(by='Win_Percentage', ascending=False).reset_index()
    return standings

# Streamlit UI
st.title("🏀 Classificação Atual da NBA - Temporada 2024-25")

# Obter dados dos jogos da temporada atual (2024-25)
games_2024_25 = get_games_by_season("2024-25")

# Calcular a classificação
current_standings = calculate_standings(games_2024_25)

# Exibir a classificação agrupada por conferência
if not current_standings.empty:
    # Separar por conferência
    eastern_standings = current_standings[current_standings['TEAM_ABBREVIATION'].isin(eastern_conference_teams)]
    western_standings = current_standings[current_standings['TEAM_ABBREVIATION'].isin(western_conference_teams)]

    # Exibir tabelas
    st.subheader("📌 Conferência Leste")
    st.dataframe(eastern_standings, use_container_width=True)

    st.subheader("📌 Conferência Oeste")
    st.dataframe(western_standings, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para a temporada 2024-25.")
