import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
from scipy.stats import gumbel_r
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams
from pygam import PoissonGAM, LinearGAM
from nba_api.stats.endpoints import playergamelog
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.model_selection import train_test_split

# Encontrar o ID do Charlotte Hornets
hornets = teams.find_team_by_abbreviation('CHA')
hornets_id = hornets['id']

# Extrair os dados dos jogos para as temporadas 23-24 e 24-25
game_logs_23_24 = teamgamelog.TeamGameLog(team_id=hornets_id, season='2023-24').get_data_frames()[0]
game_logs_24_25 = teamgamelog.TeamGameLog(team_id=hornets_id, season='2024-25').get_data_frames()[0]

# Combinar os dados das duas temporadas
all_game_logs = pd.concat([game_logs_23_24, game_logs_24_25])

# Função para aplicar o Método de Gumbel
def aplicar_gumbel(dados, coluna, X):
    params = gumbel_r.fit(dados[coluna])
    mu, beta = params

    resultados = {
        "Probabilidade de marcar acima de X": 1 - gumbel_r.cdf(X, loc=mu, scale=beta),
        "Probabilidade de atingir ou exceder X": 1 - gumbel_r.cdf(X, loc=mu, scale=beta),
        "Probabilidade de atingir ou ficar abaixo de X": gumbel_r.cdf(X, loc=mu, scale=beta),
        "Proporção de valores menores ou iguais a X": gumbel_r.cdf(X, loc=mu, scale=beta),
        "Valores menores que X": np.sum(dados[coluna] < X),
        "Proporção de valores menores que X": np.mean(dados[coluna] < X)
    }
    return resultados, mu, beta

# Interface Streamlit
st.title("Análise de Eventos Extremos na NBA - Charlotte Hornets")
st.write("Modelo baseado na Distribuição de Gumbel para prever pontuação, assistências e rebotes extremos.")

# Seleção do usuário
estatistica = st.selectbox("Selecione a estatística:", ["PTS", "AST", "REB"])
X = st.number_input("Defina o valor de X:", min_value=0, value=100)

# Aplicar Gumbel
resultados, mu, beta = aplicar_gumbel(all_game_logs, estatistica, X)

# Exibir resultados
st.subheader(f"Resultados para {estatistica} com X = {X}")
for pergunta, resposta in resultados.items():
    st.write(f"**{pergunta}:** {resposta:.4f}")

# Gráfico da Distribuição de Gumbel
x = np.linspace(min(all_game_logs[estatistica]), max(all_game_logs[estatistica]), 1000)
y = gumbel_r.pdf(x, loc=mu, scale=beta)

# Criar histograma dos dados
hist_data = [all_game_logs[estatistica]]
group_labels = [estatistica]

# Criar figura com histograma e curva de Gumbel
fig = ff.create_distplot(hist_data, group_labels, show_hist=True, show_curve=False)
fig.add_scatter(x=x, y=y, mode='lines', name=f"Gumbel (μ={mu:.2f}, β={beta:.2f})")
fig.add_vline(x=X, line=dict(color="red", dash="dash"), annotation_text=f"X = {X}")

st.plotly_chart(fig)


st.title("GAMLSS: Generalized Additive Models for Location Scale and Shape - Charlotte Hornets")

# Função para coletar dados da NBA
def get_player_stats(player_id, season):
    try:
        log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        games = log.get_data_frames()[0]
        return games[['PTS', 'REB', 'AST']]
    except Exception as e:
        st.error(f"Erro ao buscar dados do jogador {player_id} para a temporada {season}: {e}")
        return pd.DataFrame()

# IDs dos jogadores
players = {
    "LaMelo Ball": 1630163,
    "Moussa Diabate": 1631217,
    "Brandon Miller": 1641705
}

# Coletar dados
seasons = ["2023-24", "2024-25"]
data = {player: pd.concat([get_player_stats(pid, season) for season in seasons], ignore_index=True) for player, pid in players.items()}

# Previsão usando GAMLSS (PoissonGAM e LinearGAM)
predictions = {}
for player, df in data.items():
    if df.empty:
        continue
    
    X = np.arange(len(df)).reshape(-1, 1)  # Índice do jogo como variável preditora
    
    for stat in ['PTS', 'REB', 'AST']:
        y = df[stat]
        
        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Modelos
        gam_poisson = PoissonGAM().fit(X_train, y_train)
        gam_linear = LinearGAM().fit(X_train, y_train)
        
        # Previsão do próximo jogo
        x_next = np.array([[len(df)]])
        pred_poisson = gam_poisson.predict(x_next)[0]
        pred_linear = gam_linear.predict(x_next)[0]
        
        # Estatísticas
        mean = y.mean()
        median = y.median()
        mode = y.mode()[0]
        min_val = y.min()
        max_val = y.max()
        
        # Probabilidades acima/abaixo da média
        prob_above_mean = (y > mean).mean()
        prob_below_mean = 1 - prob_above_mean
        
        predictions[(player, stat)] = {
            "Poisson Prediction": pred_poisson,
            "Linear Prediction": pred_linear,
            "Mean": mean,
            "Median": median,
            "Mode": mode,
            "Min": min_val,
            "Max": max_val,
            "P(Above Mean)": prob_above_mean,
            "P(Below Mean)": prob_below_mean
        }

# Criar DataFrame de previsões
pred_df = pd.DataFrame(predictions).T
st.dataframe(pred_df)

# Gráficos de probabilidade predita e coeficientes
st.subheader("Gráficos de Probabilidade Predita")
fig_prob_pred = go.Figure()
for player, df in data.items():
    if df.empty:
        continue
    
    for stat in ['PTS', 'REB', 'AST']:
        y = df[stat]
        X = np.arange(len(df)).reshape(-1, 1)
        
        # Modelos
        gam_poisson = PoissonGAM().fit(X, y)
        gam_linear = LinearGAM().fit(X, y)
        
        # Probabilidade predita
        y_pred_poisson = gam_poisson.predict(X)
        y_pred_linear = gam_linear.predict(X)
        
        fig_prob_pred.add_trace(go.Scatter(x=np.arange(len(df)), y=y_pred_poisson, mode='lines', name=f"{player} - {stat} (Poisson)"))
        fig_prob_pred.add_trace(go.Scatter(x=np.arange(len(df)), y=y_pred_linear, mode='lines', name=f"{player} - {stat} (Linear)"))
st.plotly_chart(fig_prob_pred)

# Gráficos de Coeficientes
st.subheader("Gráficos de Coeficientes do Modelo")
fig_coef = go.Figure()
for player, df in data.items():
    if df.empty:
        continue
    
    for stat in ['PTS', 'REB', 'AST']:
        X = np.arange(len(df)).reshape(-1, 1)
        
        # Modelos
        gam_poisson = PoissonGAM().fit(X, df[stat])
        gam_linear = LinearGAM().fit(X, df[stat])
        
        # Coeficientes
        coef_poisson = gam_poisson.coef_
        coef_linear = gam_linear.coef_
        
        fig_coef.add_trace(go.Scatter(x=np.arange(len(coef_poisson)), y=coef_poisson, mode='lines', name=f"{player} - {stat} (Poisson Coefficients)"))
        fig_coef.add_trace(go.Scatter(x=np.arange(len(coef_linear)), y=coef_linear, mode='lines', name=f"{player} - {stat} (Linear Coefficients)"))
st.plotly_chart(fig_coef)

# Matriz de Confusão
st.subheader("Matriz de Confusão")
fig_confusion = go.Figure()
for player, df in data.items():
    if df.empty:
        continue
    
    for stat in ['PTS', 'REB', 'AST']:
        y_true = (df[stat] > df[stat].mean()).astype(int)  # 1 se acima da média, 0 caso contrário
        y_pred = (PoissonGAM().fit(np.arange(len(df)).reshape(-1, 1), df[stat]).predict(np.arange(len(df)).reshape(-1, 1)) > df[stat].mean()).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        
        fig_confusion.add_trace(go.Heatmap(z=cm, x=['Below', 'Above'], y=['Below', 'Above'], colorscale='Blues', name=f"{player} - {stat}"))
st.plotly_chart(fig_confusion)

# Curva ROC e AUC
st.subheader("Curva ROC e AUC")
fig_roc = go.Figure()
for player, df in data.items():
    if df.empty:
        continue
    
    for stat in ['PTS', 'REB', 'AST']:
        y_true = (df[stat] > df[stat].mean()).astype(int)
        y_scores = PoissonGAM().fit(np.arange(len(df)).reshape(-1, 1), df[stat]).predict(np.arange(len(df)).reshape(-1, 1))
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        auc_score = auc(fpr, tpr)
        
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f"{player} - {stat} (AUC={auc_score:.2f})"))
st.plotly_chart(fig_roc)
