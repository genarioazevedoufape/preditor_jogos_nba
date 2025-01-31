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

# Função para calcular os totais de vitórias e derrotas
def calculate_team_totals(team_games):
    if team_games.empty:
        return {}

    team_games['Home/Away'] = team_games['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')

    totals = {
        "Total Wins": (team_games['WL'] == 'W').sum(),
        "Total Home Wins": ((team_games['WL'] == 'W') & (team_games['Home/Away'] == 'Home')).sum(),
        "Total Away Wins": ((team_games['WL'] == 'W') & (team_games['Home/Away'] == 'Away')).sum(),
        "Total Losses": (team_games['WL'] == 'L').sum(),
        "Total Home Losses": ((team_games['WL'] == 'L') & (team_games['Home/Away'] == 'Home')).sum(),
        "Total Away Losses": ((team_games['WL'] == 'L') & (team_games['Home/Away'] == 'Away')).sum(),
    }
    return totals

# Configuração do Streamlit
st.title("🏀 Estatísticas de Times da NBA - Temporadas 2023-24 e 2024-25")

# Seleção do time
team_abbreviation = st.selectbox("Selecione um time:", options=list(nba_teams.keys()), format_func=lambda x: nba_teams[x])

# Seleção da temporada
season_options = ["2023-24", "2024-25", "Todas as Temporadas"]
selected_season = st.selectbox("Selecione a temporada:", season_options)

# Buscar jogos das temporadas 2023-24 e 2024-25
games_2023_24 = get_team_games(team_abbreviation, "2023-24")
games_2024_25 = get_team_games(team_abbreviation, "2024-25")

# Filtrar os dados com base na temporada selecionada
if selected_season == "2023-24":
    all_games = games_2023_24
elif selected_season == "2024-25":
    all_games = games_2024_25
else:
    all_games = pd.concat([games_2023_24, games_2024_25])

# Calcular os totais
team_totals = calculate_team_totals(all_games)

# Exibir os resultados
if team_totals:
    st.subheader(f"📊 {nba_teams[team_abbreviation]} - Totais na Temporada {selected_season}")
    
    # Criar dataframe para exibição
    totals_df = pd.DataFrame(team_totals.items(), columns=["Categoria", "Valor"])
    st.dataframe(totals_df, use_container_width=True)

    # Exibir gráfico de barras
    st.bar_chart(totals_df.set_index("Categoria"))
else:
    st.warning(f"Nenhum dado encontrado para o {nba_teams[team_abbreviation]} na temporada {selected_season}.")

# Processamento dos dados
if not all_games.empty:
    all_games["Home"] = all_games["MATCHUP"].apply(lambda x: "Home" if "vs." in x else "Away")
    all_games["Win"] = all_games["WL"].apply(lambda x: 1 if x == "W" else 0)
    all_games["Loss"] = all_games["WL"].apply(lambda x: 1 if x == "L" else 0)
    all_games["Points_Scored"] = all_games["PTS"]
    all_games["Points_Allowed"] = all_games["PTS"] - all_games["PLUS_MINUS"]

    # Estatísticas para gráficos
    wins = all_games["Win"].sum()
    losses = all_games["Loss"].sum()
    wins_home = all_games[all_games["Home"] == "Home"]["Win"].sum()
    wins_away = all_games[all_games["Home"] == "Away"]["Win"].sum()
    losses_home = all_games[all_games["Home"] == "Home"]["Loss"].sum()
    losses_away = all_games[all_games["Home"] == "Away"]["Loss"].sum()

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
    fig3 = px.histogram(all_games, x="WL", nbins=2, color="WL", color_discrete_map={"W": "green", "L": "red"})
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

    # Gráfico 5: Gráfico de Linhas (Sequência de Vitórias e Derrotas)
    st.subheader("Sequência de Vitórias e Derrotas")

    # Adicionar uma coluna para o número do jogo
    all_games["Game_Number"] = range(1, len(all_games) + 1)

    # Criar uma coluna para o resultado do jogo (Vitória ou Derrota)
    all_games["Result"] = all_games["WL"].apply(lambda x: "Vitória" if x == "W" else "Derrota")

    # Criar o gráfico de linhas
    fig5 = go.Figure()

    # Adicionar linha para vitórias
    fig5.add_trace(
        go.Scatter(
            x=all_games["Game_Number"],
            y=all_games["Win"],
            mode='lines+markers',
            name="Vitórias",
            line=dict(color="green"),
            marker=dict(symbol="circle", size=8)
        )
    )

    # Adicionar linha para derrotas
    fig5.add_trace(
        go.Scatter(
            x=all_games["Game_Number"],
            y=all_games["Loss"],
            mode='lines+markers',
            name="Derrotas",
            line=dict(color="red"),
            marker=dict(symbol="x", size=8)
        )
    )

    # Configurações do layout
    fig5.update_layout(
        title="Sequência de Vitórias e Derrotas",
        xaxis_title="Número do Jogo",
        yaxis_title="Resultado",
        yaxis=dict(
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["Derrota", "Vitória"]
        ),
        legend_title="Resultado",
        hovermode="x unified"
    )

    # Exibir o gráfico
    st.plotly_chart(fig5)