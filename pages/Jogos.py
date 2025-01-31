import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

# Lista de times da NBA
nba_teams = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets", "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers", "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons", "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies", "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves", "NOP": "New Orleans Pelicans", "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder", "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs", "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz", "WAS": "Washington Wizards"
}

# Função para buscar jogos por temporada de um time específico
def get_team_games(team_abbreviation, season):
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        games = gamefinder.get_data_frames()[0]
        return games[games['TEAM_ABBREVIATION'] == team_abbreviation]
    except Exception as e:
        st.error(f"Erro ao buscar jogos para {team_abbreviation} na temporada {season}: {e}")
        return pd.DataFrame()

# Função para formatar e exibir os jogos com as informações solicitadas
def display_team_games(team_games):
    if team_games.empty:
        return pd.DataFrame()

    team_games['GAME_DATE'] = pd.to_datetime(team_games['GAME_DATE'])
    team_games['OPPONENT'] = team_games['MATCHUP'].apply(lambda x: x.split(' ')[2] if len(x.split(' ')) > 2 else x.split(' ')[0])
    team_games['LOCATION'] = team_games['MATCHUP'].apply(lambda x: 'Casa' if 'vs' in x else 'Fora')
    team_games['RESULT'] = team_games['WL'].apply(lambda x: 'Vitória' if x == 'W' else 'Derrota')
    
    # Selecionar as colunas relevantes
    relevant_columns = ['GAME_DATE', 'OPPONENT', 'RESULT', 'LOCATION', 'PTS']
    team_games = team_games[relevant_columns]
    return team_games

# Configuração do Streamlit
st.title("🏀 Informações dos Jogos da NBA - Temporadas 2023-24 e 2024-25")

# Seleção do time
team_abbreviation = st.selectbox("Selecione um time:", options=list(nba_teams.keys()), format_func=lambda x: nba_teams[x])

# Buscar jogos das temporadas 2023-24 e 2024-25
games_2023_24 = get_team_games(team_abbreviation, "2023-24")
games_2024_25 = get_team_games(team_abbreviation, "2024-25")

# Concatenar os jogos das duas temporadas
all_games = pd.concat([games_2023_24, games_2024_25])

# Formatar os dados dos jogos
team_games_display = display_team_games(all_games)

# Exibir os dados no Streamlit
if not team_games_display.empty:
    st.subheader(f"📊 Jogos do {nba_teams[team_abbreviation]} (2023-24 e 2024-25)")
    st.dataframe(team_games_display, use_container_width=True)

    # Gráfico de Pontos por Jogo
    st.subheader("Gráfico de Pontuação por Jogo")
    st.line_chart(data=team_games_display.set_index('GAME_DATE')['PTS'])
else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} nas temporadas selecionadas.")
