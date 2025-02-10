import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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


# Função para calcular a performance defensiva por temporada
def calculate_defensive_performance_by_season(team_games_2023_24, team_games_2024_25):
    defensive_performance_2023_24 = {
        "Total Steals": team_games_2023_24['STL'].sum(),
        "Total Defensive Rebounds": team_games_2023_24['DREB'].sum(),
        "Average Blocks per Game": team_games_2023_24['BLK'].mean(),
        "Average Turnovers per Game": team_games_2023_24['TOV'].mean(),
        "Average Personal Fouls per Game": team_games_2023_24['PF'].mean()
    }

    defensive_performance_2024_25 = {
        "Total Steals": team_games_2024_25['STL'].sum(),
        "Total Defensive Rebounds": team_games_2024_25['DREB'].sum(),
        "Average Blocks per Game": team_games_2024_25['BLK'].mean(),
        "Average Turnovers per Game": team_games_2024_25['TOV'].mean(),
        "Average Personal Fouls per Game": team_games_2024_25['PF'].mean()
    }

    return defensive_performance_2023_24, defensive_performance_2024_25

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

# Função para calcular os totais de rebotes e pontuações por temporada
def calculate_rebounds_and_scoring_by_season(team_games_2023_24, team_games_2024_25):
    if team_games_2023_24.empty and team_games_2024_25.empty:
        return {}, {}

    totals_2023_24 = {
        "Total Rebounds": team_games_2023_24['REB'].sum(),
        "Total Offensive Rebounds": team_games_2023_24['OREB'].sum(),
        "Total Defensive Rebounds": team_games_2023_24['DREB'].sum(),
        "Total Points": team_games_2023_24['PTS'].sum(),
        "Total 2-Point Field Goals Made": (team_games_2023_24['FGM'] - team_games_2023_24['FG3M']).sum(),
        "Total 3-Point Field Goals Made": team_games_2023_24['FG3M'].sum(),
        "Total Free Throws Made": team_games_2023_24['FTM'].sum()
    }

    totals_2024_25 = {
        "Total Rebounds": team_games_2024_25['REB'].sum(),
        "Total Offensive Rebounds": team_games_2024_25['OREB'].sum(),
        "Total Defensive Rebounds": team_games_2024_25['DREB'].sum(),
        "Total Points": team_games_2024_25['PTS'].sum(),
        "Total 2-Point Field Goals Made": (team_games_2024_25['FGM'] - team_games_2024_25['FG3M']).sum(),
        "Total 3-Point Field Goals Made": team_games_2024_25['FG3M'].sum(),
        "Total Free Throws Made": team_games_2024_25['FTM'].sum()
    }

    return totals_2023_24, totals_2024_25

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

# Calcular a performance defensiva por temporada
defensive_performance_2023_24, defensive_performance_2024_25 = calculate_defensive_performance_by_season(games_2023_24, games_2024_25)

# Exibir performance defensiva por temporada
if defensive_performance_2023_24 or defensive_performance_2024_25:
    st.subheader(f"📊 {nba_teams[team_abbreviation]} - Performance Defensiva por Temporada (2023-24 vs 2024-25)")

    # Criar dataframes para exibição
    performance_2023_24_df = pd.DataFrame(defensive_performance_2023_24.items(), columns=["Categoria", "2023-24"])
    performance_2024_25_df = pd.DataFrame(defensive_performance_2024_25.items(), columns=["Categoria", "2024-25"])

    # Mesclar os dataframes de forma a ter as categorias lado a lado
    comparison_df = pd.merge(performance_2023_24_df, performance_2024_25_df, on="Categoria")

    # Adicionar a coluna 'Total'
    comparison_df['Total'] = comparison_df['2023-24'] + comparison_df['2024-25']

    st.dataframe(comparison_df, use_container_width=True)

    # Exibir gráfico de barras comparativo
    fig = go.Figure()

    # Barra para 2023-24
    fig.add_trace(go.Bar(
        y=comparison_df["Categoria"],
        x=comparison_df["2023-24"],
        name="2023-24",
        orientation="h",
        marker_color='blue'
    ))

    # Barra para 2024-25
    fig.add_trace(go.Bar(
        y=comparison_df["Categoria"],
        x=comparison_df["2024-25"],
        name="2024-25",
        orientation="h",
        marker_color='green'
    ))

    # Barra para Total
    # fig.add_trace(go.Bar(
    #     y=comparison_df["Categoria"],
    #     x=comparison_df["Total"],
    #     name="Total",
    #     orientation="h",
    #     marker_color='purple'
    # ))

    # Ajuste de layout
    fig.update_layout(
        title=f"Comparativo de Performance Defensiva - {nba_teams[team_abbreviation]} (2023-24 vs 2024-25)",
        xaxis_title='Valor',
        yaxis_title='Categoria',
        barmode='group',
        template='plotly_dark'
    )

    st.plotly_chart(fig)
else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} nas temporadas 2023-24 e 2024-25.")

# Calcular os totais de rebotes e pontuações para as duas temporadas
rebounds_and_scoring_totals_2023_24, rebounds_and_scoring_totals_2024_25 = calculate_rebounds_and_scoring_by_season(games_2023_24, games_2024_25)

# Exibir os resultados de rebotes e pontuações
if rebounds_and_scoring_totals_2023_24 or rebounds_and_scoring_totals_2024_25:
    st.subheader(f"📊 {nba_teams[team_abbreviation]} - Comparativo de Rebotes e Pontuações (2023-24 e 2024-25)")

    # Criar dataframes para exibição
    totals_2023_24_df = pd.DataFrame(rebounds_and_scoring_totals_2023_24.items(), columns=["Categoria", "2023-24"])
    totals_2024_25_df = pd.DataFrame(rebounds_and_scoring_totals_2024_25.items(), columns=["Categoria", "2024-25"])

    # Mesclar os dataframes de forma a ter as categorias lado a lado
    comparison_df = pd.merge(totals_2023_24_df, totals_2024_25_df, on="Categoria")

    # Adicionar a coluna 'Total'
    comparison_df['Total'] = comparison_df['2023-24'] + comparison_df['2024-25']

    st.dataframe(comparison_df, use_container_width=True)

    # Exibir gráfico de barras comparativo
    fig = go.Figure()

    # Barra para 2023-24
    fig.add_trace(go.Bar(
        y=comparison_df["Categoria"],
        x=comparison_df["2023-24"],
        name="2023-24",
        orientation="h",
        marker_color='blue'
    ))

    # Barra para 2024-25
    fig.add_trace(go.Bar(
        y=comparison_df["Categoria"],
        x=comparison_df["2024-25"],
        name="2024-25",
        orientation="h",
        marker_color='green'
    ))

    # Barra para Total
    # fig.add_trace(go.Bar(
    #     y=comparison_df["Categoria"],
    #     x=comparison_df["Total"],
    #     name="Total",
    #     orientation="h",
    #     marker_color='purple'
    # ))

    # Ajuste de layout
    fig.update_layout(
        title=f"Comparativo de Rebotes e Pontuações - {nba_teams[team_abbreviation]} (2023-24 vs 2024-25)",
        xaxis_title='Valor',
        yaxis_title='Categoria',
        barmode='group',
        template='plotly_dark'
    )

    st.plotly_chart(fig)
else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} nas temporadas 2023-24 e 2024-25.")
