import streamlit as st
import pandas as pd
import plotly.express as px
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

# Função para calcular estatísticas do time
def calculate_team_stats(team_games):
    if team_games.empty:
        return {}

    team_games['Home/Away'] = team_games['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')

    stats = {
        "Points per Game": team_games['PTS'].mean(),
        "Assists per Game": team_games['AST'].mean(),
        "Rebounds per Game": team_games['REB'].mean(),
        "3-Point Field Goals Made": team_games['FG3M'].sum(),
        "Total Home Losses": ((team_games['WL'] == 'L') & (team_games['Home/Away'] == 'Home')).sum(),
        "Total Away Losses": ((team_games['WL'] == 'L') & (team_games['Home/Away'] == 'Away')).sum()
    }
    return stats

# Função para calcular a média de pontos marcados e sofridos por time
def calculate_team_points_averages(season):
    team_averages = [
        {
            "Team": team_name,
            "Avg Points Scored": games['PTS'].mean(),
            "Avg Points Allowed": (games['PTS'] - games['PLUS_MINUS']).mean()
        }
        for team_abbreviation, team_name in nba_teams.items()
        if not (games := get_team_games(team_abbreviation, season)).empty
    ]
    return pd.DataFrame(team_averages)


# Configuração do Streamlit
st.title("🏀 Estatísticas de Times da NBA - Temporadas 2023-24 e 2024-25")

# Seleção do time
team_abbreviation = st.selectbox("Selecione um time:", options=list(nba_teams.keys()), format_func=lambda x: nba_teams[x])

# Seleção da temporada
season_options = ["2023-24", "2024-25"]
selected_season = st.selectbox("Selecione a temporada:", season_options)

# Buscar jogos da temporada selecionada
games = get_team_games(team_abbreviation, selected_season)

# Calcular estatísticas
team_stats = calculate_team_stats(games)

# Exibir os resultados
if team_stats:
    st.subheader(f"📊 {nba_teams[team_abbreviation]} - Estatísticas na Temporada {selected_season}")
    
    # Criar dataframe para exibição
    stats_df = pd.DataFrame(team_stats.items(), columns=["Categoria", "Valor"])
    stats_df['Valor'] = stats_df['Valor'].round(2)
    st.dataframe(stats_df, use_container_width=True)

    # Exibir gráfico de barras
    st.bar_chart(stats_df.set_index("Categoria"))
# else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} na temporada {selected_season}.")

# Processamento dos dados para o gráfico de radar
if not games.empty:
    games["Home"] = games["MATCHUP"].apply(lambda x: "Home" if "vs." in x else "Away")
    games["Points_Scored"] = games["PTS"]
    games["Points_Allowed"] = games["PTS"] - games["PLUS_MINUS"]

    # Gráfico 5: Radar (Média de Pontos Marcados/Sofridos)
    st.subheader("Média de Pontos Marcados e Sofridos")
    stats = [
        games[games["Home"] == "Home"]["Points_Scored"].mean(),
        games[games["Home"] == "Home"]["Points_Allowed"].mean(),
        games[games["Home"] == "Away"]["Points_Scored"].mean(),
        games[games["Home"] == "Away"]["Points_Allowed"].mean()
    ]
    labels = ["Pontos Marcados (Casa)", "Pontos Sofridos (Casa)", "Pontos Marcados (Fora)", "Pontos Sofridos (Fora)"]
    fig5 = go.Figure(data=go.Scatterpolar(
        r=stats + stats[:1],  # Fechar o círculo
        theta=labels + labels[:1],  # Fechar o círculo
        fill='toself',
        name="Média de Pontos"
    ))
    fig5.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(stats) + 10]  # Ajustar o range para melhor visualização
            )
        ),
        showlegend=True
    )
    st.plotly_chart(fig5)

# Gráfico de Dispersão: Média de Pontos Marcados vs Sofridos por Time
st.subheader("Gráfico de Dispersão: Média de Pontos Marcados vs Sofridos")
team_averages_df = calculate_team_points_averages(selected_season)

# Verificar se há dados para exibir
if not team_averages_df.empty:
    st.write("Dados coletados para o gráfico de dispersão:")
    st.dataframe(team_averages_df)  # Exibir os dados coletados para depuração

    # Criar o gráfico de dispersão
    fig6 = px.scatter(
        team_averages_df,
        x="Avg Points Scored",
        y="Avg Points Allowed",
        text="Team",
        title=f"Média de Pontos Marcados vs Sofridos na Temporada {selected_season}",
        labels={
            "Avg Points Scored": "Média de Pontos Marcados",
            "Avg Points Allowed": "Média de Pontos Sofridos"
        }
    )
    fig6.update_traces(textposition='top center')
    st.plotly_chart(fig6)
# else:
    st.warning("Nenhum dado encontrado para exibir o gráfico de dispersão.")