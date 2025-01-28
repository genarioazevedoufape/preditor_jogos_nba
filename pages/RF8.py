import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams

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

# Função para obter o ID do time com base na abreviação
def get_team_id(team_abbreviation):
    team = teams.find_team_by_abbreviation(team_abbreviation)
    return team["id"]

# Função para obter os jogos de uma temporada
def get_team_games(team_id, season):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_nullable=season)
    games = gamefinder.get_data_frames()[0]
    return games

# Streamlit App
st.title("Análise de Desempenho de Times da NBA")

# Seleção do time
selected_team_abbreviation = st.selectbox("Selecione o time:", list(nba_teams.keys()), format_func=lambda x: nba_teams[x])
team_id = get_team_id(selected_team_abbreviation)

# Seleção da temporada
season_options = ["2023-24", "2024-25", "Todas as Temporadas"]
selected_season = st.selectbox("Selecione a temporada:", season_options)

# Obtendo os jogos da temporada selecionada
if selected_season == "Todas as Temporadas":
    # Busca os dados de todas as temporadas disponíveis
    games_list = []
    for season in season_options[:-1]:  # Ignora a última opção ("Todas as Temporadas")
        games = get_team_games(team_id, season)
        games_list.append(games)
    games = pd.concat(games_list, ignore_index=True)
else:
    games = get_team_games(team_id, selected_season)

# Processamento dos dados
if not games.empty:
    games["Home"] = games["MATCHUP"].apply(lambda x: "Home" if "vs." in x else "Away")
    games["Win"] = games["WL"].apply(lambda x: 1 if x == "W" else 0)
    games["Loss"] = games["WL"].apply(lambda x: 1 if x == "L" else 0)
    games["Points_Scored"] = games["PTS"]
    games["Points_Allowed"] = games["PTS"] - games["PLUS_MINUS"]

    # Estatísticas para gráficos
    wins = games["Win"].sum()
    losses = games["Loss"].sum()
    wins_home = games[games["Home"] == "Home"]["Win"].sum()
    wins_away = games[games["Home"] == "Away"]["Win"].sum()
    losses_home = games[games["Home"] == "Home"]["Loss"].sum()
    losses_away = games[games["Home"] == "Away"]["Loss"].sum()

    # Gráfico 1: Barras Empilhadas de Vitórias e Derrotas
    st.subheader("Vitórias e Derrotas Totais")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(name="Vitórias", x=["Total"], y=[wins], marker_color="green"))
    fig1.add_trace(go.Bar(name="Derrotas", x=["Total"], y=[losses], marker_color="red"))
    fig1.update_layout(barmode="stack", title="Vitórias e Derrotas Totais", xaxis_title="", yaxis_title="Quantidade")
    st.plotly_chart(fig1)

    # Gráfico 2: Barras Agrupadas (Vitórias e Derrotas em Casa/Fora)
    st.subheader("Vitórias e Derrotas - Casa vs Fora")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=["Casa", "Fora"], y=[wins_home, wins_away], name="Vitórias", marker_color="green"))
    fig2.add_trace(go.Bar(x=["Casa", "Fora"], y=[losses_home, losses_away], name="Derrotas", marker_color="red"))
    st.plotly_chart(fig2)

    # Gráfico 3: Histograma de Vitórias e Derrotas
    st.subheader("Frequência de Vitórias e Derrotas")
    fig3 = px.histogram(games, x="WL", nbins=2, color="WL", color_discrete_map={"W": "green", "L": "red"})
    st.plotly_chart(fig3)

    # Gráfico 4: Gráfico de Pizza
    st.subheader("Distribuição de Vitórias e Derrotas")
    data_pizza = {
        "Categoria": ["Vitórias Casa", "Vitórias Fora", "Derrotas Casa", "Derrotas Fora"],
        "Quantidade": [wins_home, wins_away, losses_home, losses_away],
    }
    df_pizza = pd.DataFrame(data_pizza)
    fig4 = px.pie(df_pizza, names="Categoria", values="Quantidade", title="Distribuição de Vitórias e Derrotas",
                  color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig4)

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
        r=stats + stats[:1],
        theta=labels + labels[:1],
        fill='toself'
    ))
    st.plotly_chart(fig5)

    # Gráfico 6: Gráfico de Linhas (Sequência de Vitórias e Derrotas)
    st.subheader("Sequência de Vitórias e Derrotas")
    games["Game_Number"] = range(1, len(games) + 1)
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=games["Game_Number"], y=games["Win"], mode='lines+markers', name="Vitórias", line=dict(color="green")))
    fig6.add_trace(go.Scatter(x=games["Game_Number"], y=games["Loss"], mode='lines+markers', name="Derrotas", line=dict(color="red")))
    st.plotly_chart(fig6)

    # Gráfico 7: Gráfico de Dispersão (Média de Pontos por Equipe)
    st.subheader("Dispersão de Equipes na Temporada")
    team_avg_points = games.groupby("TEAM_NAME")[["Points_Scored", "Points_Allowed"]].mean()
    fig7 = px.scatter(team_avg_points, x="Points_Scored", y="Points_Allowed", color=team_avg_points.index)
    fig7.add_hline(y=games["Points_Allowed"].mean(), line_dash="dash", line_color="red", annotation_text="Média Pontos Sofridos")
    fig7.add_vline(x=games["Points_Scored"].mean(), line_dash="dash", line_color="blue", annotation_text="Média Pontos Marcados")
    st.plotly_chart(fig7)

else:
    st.warning("Nenhum jogo encontrado para o time e temporada selecionados.")