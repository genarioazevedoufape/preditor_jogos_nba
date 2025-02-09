import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leaguegamefinder, leaguestandings, playercareerstats, playergamelog

# Configuração da página
st.set_page_config(
    page_title="Charlotte Hornets",
    page_icon="img/Charlotte_Hornets.png",
    layout="wide",
)

# Layout do título com logo
col1, col2 = st.columns([1, 8])
with col1:
    st.image("img/Charlotte_Hornets.png", width=100)
with col2:
    st.title("Charlotte Hornets")

# Expander com informações sobre o time
with st.expander("Saiba mais"):
    st.write('''O Charlotte Hornets é um time norte-americano de basquete profissional com sede em Charlotte, Carolina do Norte. 
             Os Hornets competem na National Basketball Association (NBA) como um membro da Divisão Sudeste da Conferência Leste.''')

# Função para buscar estatísticas de jogos por temporada
def get_team_stats(team_id, season):
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_nullable=season)
        games = gamefinder.get_data_frames()[0]
        
        total_wins = (games['WL'] == 'W').sum()
        total_losses = (games['WL'] == 'L').sum()
        home_wins = ((games['WL'] == 'W') & (games['MATCHUP'].str.contains('vs'))).sum()
        away_wins = ((games['WL'] == 'W') & (games['MATCHUP'].str.contains('@'))).sum()
        home_losses = ((games['WL'] == 'L') & (games['MATCHUP'].str.contains('vs'))).sum()
        away_losses = ((games['WL'] == 'L') & (games['MATCHUP'].str.contains('@'))).sum()
        
        return {
            "Total Vitórias": total_wins,
            "Vitórias em Casa": home_wins,
            "Vitórias Fora": away_wins,
            "Total Derrotas": total_losses,
            "Derrotas em Casa": home_losses,
            "Derrotas Fora": away_losses
        }
    except Exception as e:
        st.error(f"Erro ao buscar dados da temporada {season}: {e}")
        return {}

# Função para obter a classificação atual do Charlotte Hornets
def get_team_standings(team_id):
    try:
        standings = leaguestandings.LeagueStandings().get_data_frames()[0]
        team_standings = standings[standings['TeamID'] == team_id]

        if team_standings.empty:
            st.warning("Dados de classificação não encontrados para o Charlotte Hornets.")
            return None

        return team_standings.iloc[0]
    except Exception as e:
        st.error(f"Erro ao buscar a classificação: {e}")
        return None

# ID do Charlotte Hornets (Corrigido para inteiro)
charlotte_hornets_id = 1610612766

# Coletar dados da temporada 2024-25
season = "2024-25"
stats = get_team_stats(charlotte_hornets_id, season)

# Exibir métricas
st.subheader("📊 Desempenho na Temporada 2024-25")
if stats:
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    col1.metric("Total de Vitórias", stats["Total Vitórias"])
    col2.metric("Vitórias em Casa", stats["Vitórias em Casa"])
    col3.metric("Vitórias Fora", stats["Vitórias Fora"])
    col4.metric("Total de Derrotas", stats["Total Derrotas"])
    col5.metric("Derrotas em Casa", stats["Derrotas em Casa"])
    col6.metric("Derrotas Fora", stats["Derrotas Fora"])
else:
    st.warning(f"Dados não disponíveis para a temporada {season}.")

# Exibir a classificação atual do Charlotte Hornets
st.subheader("🏆 Classificação Atual")
team_standings = get_team_standings(charlotte_hornets_id)

if team_standings is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Posição na Conferência Leste:** {team_standings.get('ConferenceRank', 'N/A')}")
    with col2:
        st.write(f"**Recorde:** {team_standings.get('WINS', 0)}-{team_standings.get('LOSSES', 0)}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Porcentagem de Vitórias:** {team_standings.get('WinPCT', 0.0):.3f}")
    with col2:
        st.write(f"**Últimos 10 Jogos:** {team_standings.get('L10', 'N/A')}")
else:
    st.warning("Não foi possível obter a classificação atual do Charlotte Hornets.")

# Dicionário associando IDs aos nomes
player_info = {
    1630163: "LaMelo Ball",
    1631217: "Moussa Diabate",
    1641706: "Brandon Miller"
}

# Lista para armazenar as estatísticas
career_stats_list = []

for player_id in player_info.keys():
    # Obtendo estatísticas totais da carreira
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
    career_totals = career_stats[career_stats["SEASON_ID"] == "Career"]

    if career_totals.empty:
        career_totals = career_stats[career_stats["LEAGUE_ID"] == "00"].sum(numeric_only=True)
    else:
        career_totals = career_totals.iloc[0]

    # Obtendo o log de jogos da temporada atual
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season="2023-24").get_data_frames()[0]

    game_log["HOME"] = game_log["MATCHUP"].apply(lambda x: "Casa" if "vs." in x else "Fora")

    # Estatísticas separadas para casa e fora
    casa_stats = game_log[game_log["HOME"] == "Casa"]
    fora_stats = game_log[game_log["HOME"] == "Fora"]

    # Calcular médias
    pts_casa_media = casa_stats["PTS"].mean() if len(casa_stats) > 0 else 0
    pts_fora_media = fora_stats["PTS"].mean() if len(fora_stats) > 0 else 0
    reb_casa_media = casa_stats["REB"].mean() if len(casa_stats) > 0 else 0
    reb_fora_media = fora_stats["REB"].mean() if len(fora_stats) > 0 else 0
    ast_casa_media = casa_stats["AST"].mean() if len(casa_stats) > 0 else 0
    ast_fora_media = fora_stats["AST"].mean() if len(fora_stats) > 0 else 0

    # Estatísticas da temporada atual
    pts_media_temporada = game_log["PTS"].mean()
    reb_media_temporada = game_log["REB"].mean()
    ast_media_temporada = game_log["AST"].mean()

    # Adicionando ao DataFrame
    career_stats_list.append({
        "Jogador": player_info[player_id],
        "PTS Carreira": int(career_totals["PTS"]),
        "REB Carreira": int(career_totals["REB"]),
        "AST Carreira": int(career_totals["AST"]),
        "PTS Média Temporada Atual": pts_media_temporada,
        "REB Média Temporada Atual": reb_media_temporada,
        "AST Média Temporada Atual": ast_media_temporada,
        "PTS Casa Média": pts_casa_media,
        "PTS Fora Média": pts_fora_media,
    })

# Exibir as estatísticas dos jogadores
df_career_stats = pd.DataFrame(career_stats_list)

# Exibir o DataFrame no Streamlit
st.subheader("🏀 Estatísticas de Carreira dos Jogadores")
st.dataframe(df_career_stats)

# Gráfico para comparar pontos por jogo de cada jogador usando Plotly
# Definindo uma nova paleta de cores
new_color_palette = px.colors.qualitative.Plotly

# Gráfico com uma nova paleta de cores
fig = px.bar(df_career_stats, 
             x="Jogador", 
             y="PTS Média Temporada Atual", 
             title="Pontos Médios na Temporada Atual por Jogador",
             labels={"PTS Média Temporada Atual": "Pontos Médios", "Jogador": "Jogador"},
             color="Jogador",  # Definir a variável de cor
             color_discrete_sequence=new_color_palette)  # Aplicando a nova paleta de cores

st.plotly_chart(fig)