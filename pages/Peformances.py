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

# Função para calcular a performance defensiva
def calculate_defensive_performance(team_games):
    if team_games.empty:
        return {}

    defensive_performance = {
        "Total Steals": team_games['STL'].sum(),
        "Total Defensive Rebounds": team_games['DREB'].sum(),
        "Average Blocks per Game": team_games['BLK'].mean(),
        "Average Turnovers per Game": team_games['TOV'].mean(),
        "Average Personal Fouls per Game": team_games['PF'].mean()
    }
    return defensive_performance

# Função para calcular a divisão de dados (rebotes e pontuações)
def calculate_rebounds_and_scoring(team_games):
    if team_games.empty:
        return {}

    totals = {
        "Total Rebounds": team_games['REB'].sum(),
        "Total Offensive Rebounds": team_games['OREB'].sum(),
        "Total Defensive Rebounds": team_games['DREB'].sum(),
        "Total Points": team_games['PTS'].sum(),
        "Total 2-Point Field Goals Made": (team_games['FGM'] - team_games['FG3M']).sum(),
        "Total 3-Point Field Goals Made": team_games['FG3M'].sum(),
        "Total Free Throws Made": team_games['FTM'].sum()
    }
    return totals

# Configuração do Streamlit
st.title("🏀 Performance Times da NBA - Temporadas 2023-24 e 2024-25")

# Seleção do time
team_abbreviation = st.selectbox("Selecione um time:", options=list(nba_teams.keys()), format_func=lambda x: nba_teams[x])

# Buscar jogos das temporadas 2023-24 e 2024-25
games_2023_24 = get_team_games(team_abbreviation, "2023-24")
games_2024_25 = get_team_games(team_abbreviation, "2024-25")

# Concatenar os jogos das duas temporadas
all_games = pd.concat([games_2023_24, games_2024_25])

# Calcular a performance defensiva
defensive_performance_totals = calculate_defensive_performance(all_games)

# Exibir gráfico de barras horizontais para performance defensiva
if defensive_performance_totals:
    st.subheader(f"📊 {nba_teams[team_abbreviation]} - Performance Defensiva (2023-24 e 2024-25)")

    # Criar dataframe para exibição
    performance_df = pd.DataFrame(defensive_performance_totals.items(), columns=["Categoria", "Valor"])
    performance_df["Valor"] = performance_df["Valor"].apply(lambda x: f"{x:.2f}" if isinstance(x, float) else int(x))
    st.dataframe(performance_df, use_container_width=True)

    # Exibir gráfico de barras horizontais
    st.bar_chart(performance_df.set_index("Categoria")["Valor"].astype(float), use_container_width=True)
else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} nas temporadas 2023-24 e 2024-25.")


# Calcular os totais
rebounds_and_scoring_totals = calculate_rebounds_and_scoring(all_games)

# Exibir os resultados de rebotes e pontuações
if rebounds_and_scoring_totals:
    st.subheader(f"📊 {nba_teams[team_abbreviation]} - Totais de Rebotes e Pontuações (2023-24 e 2024-25)")

    # Criar dataframe para exibição
    totals_df = pd.DataFrame(rebounds_and_scoring_totals.items(), columns=["Categoria", "Valor"])
    st.dataframe(totals_df, use_container_width=True)

    # Exibir gráfico de barras
    st.bar_chart(totals_df.set_index("Categoria"))
else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} nas temporadas 2023-24 e 2024-25.")
