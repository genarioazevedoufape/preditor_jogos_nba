import streamlit as st
import pandas as pd
from nba_api.stats.static import teams
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

# Função para listar todos os times agrupados por conferência
def get_teams_by_conference():
    nba_teams = teams.get_teams()
    
    eastern_conference = [
        {"ID": team["id"], "Nome": team["full_name"], "Sigla": team["abbreviation"], "Conferência": "Leste"}
        for team in nba_teams if team["abbreviation"] in eastern_conference_teams
    ]

    western_conference = [
        {"ID": team["id"], "Nome": team["full_name"], "Sigla": team["abbreviation"], "Conferência": "Oeste"}
        for team in nba_teams if team["abbreviation"] in western_conference_teams
    ]
    
    return eastern_conference, western_conference

# Função para buscar jogos por temporada
def get_games_by_season(season):
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        games = gamefinder.get_data_frames()[0]
        return games
    except Exception as e:
        st.error(f"Erro ao buscar jogos da temporada {season}: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio se houver erro

# Streamlit UI
st.title("🏀 Dados da NBA - Temporadas 2023-24 e 2024-25")

# Exibir os times organizados por conferência
st.subheader("Equipes da NBA por Conferência")

eastern, western = get_teams_by_conference()

st.write("### 📌 Conferência Leste")
df_eastern = pd.DataFrame(eastern)
st.dataframe(df_eastern, use_container_width=True)

st.write("### 📌 Conferência Oeste")
df_western = pd.DataFrame(western)
st.dataframe(df_western, use_container_width=True)

# Buscar e exibir os jogos das temporadas
st.subheader("📊 Jogos das Temporadas 2023-24 e 2024-25")

# Selecionar temporada
season_selected = st.selectbox("Selecione a Temporada", ["2023-24", "2024-25"])

if season_selected == "2023-24":
    games_df = get_games_by_season("2023-24")
else:
    games_df = get_games_by_season("2024-25")

# Exibir os jogos em formato de tabela
if not games_df.empty:
    st.write(f"### Jogos da Temporada {season_selected}")
    st.dataframe(games_df, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para esta temporada.")

