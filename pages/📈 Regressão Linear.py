import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from nba_api.stats.endpoints import playergamelog
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, confusion_matrix, roc_curve, auc

# 📌 Dicionário de jogadores e IDs na NBA API
players = {
    "LaMelo Ball": 1630163,
    "Brandon Miller": 1641706,
    "Moussa Diabate": 1631217
}

# 📌 Variáveis independentes (features) e dependentes (target)
features = ["MIN", "FGA", "TOV"]  # Tempo de quadra, arremessos tentados e turnovers
targets = ["PTS", "AST", "REB"]   # Pontos, assistências e rebotes

# 📌 Função para coletar dados dos jogos dos jogadores
def get_player_data(player_id, seasons):
    all_data = []
    for season in seasons:
        try:
            log = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
            log = log[["MIN", "FGA", "TOV", "PTS", "AST", "REB"]]
            all_data.append(log)
        except Exception as e:
            st.warning(f"Erro ao buscar dados para o jogador {player_id} na temporada {season}: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

# 📌 Coletar dados para os jogadores
seasons = ["2023-24", "2024-25"]
player_data = {name: get_player_data(pid, seasons) for name, pid in players.items()}

# 📌 Função para treinar o modelo de regressão linear
def train_model(df, feature_cols, target_col):
    X = df[feature_cols]
    y = df[target_col]
    
    # Divisão treino/teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, X_test, y_test, y_pred, mae, r2

# 📌 Criar interface no Streamlit
st.title("📊 Previsão de Desempenho dos Jogadores do Charlotte Hornets")

# Seleção de jogador
player_name = st.selectbox("Escolha um jogador", list(players.keys()))
player_df = player_data[player_name]

if player_df.empty:
    st.warning("Nenhum dado disponível para este jogador.")
else:
    st.write(f"📌 Dados disponíveis para {player_name}:")
    st.dataframe(player_df.head())

    # 📌 Treinar modelos para Pontos, Assistências e Rebotes
    models = {}
    metrics = {}
    predictions = {}

    for target in targets:
        model, X_test, y_test, y_pred, mae, r2 = train_model(player_df, features, target)
        models[target] = model
        metrics[target] = {"MAE": mae, "R² Score": r2}
        predictions[target] = model.predict([[30, 15, 2]])[0]  # Exemplo: 30 min, 15 FGA, 2 TOV

    # 📌 Exibir métricas do modelo
    st.subheader("📌 Métricas do Modelo")
    st.write(pd.DataFrame(metrics).T)

    # 📌 Matriz de Confusão
    st.subheader("📊 Matriz de Confusão")
    for target in targets:
        y_true = (y_test > y_test.mean()).astype(int)  # 1 se acima da média, 0 caso contrário
        y_pred_class = (y_pred > y_test.mean()).astype(int)
        cm = confusion_matrix(y_true, y_pred_class)

        fig_cm = go.Figure(data=go.Heatmap(
            z=cm,
            x=["Abaixo da Média", "Acima da Média"],
            y=["Abaixo da Média", "Acima da Média"],
            colorscale="Blues",
            text=cm,
            texttemplate="%{text}"
        ))
        fig_cm.update_layout(title=f"Matriz de Confusão - {target}")
        st.plotly_chart(fig_cm)

    # 📌 Curva ROC
    st.subheader("📊 Curva ROC e AUC")
    fig_roc = go.Figure()
    for target in targets:
        y_true = (y_test > y_test.mean()).astype(int)
        y_scores = y_pred
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        auc_score = auc(fpr, tpr)

        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f"{target} (AUC={auc_score:.2f})"))
    
    fig_roc.update_layout(title="Curva ROC", xaxis_title="Falso Positivo", yaxis_title="Verdadeiro Positivo")
    st.plotly_chart(fig_roc)

    # 📌 Gráfico de Probabilidade Predita
    st.subheader("📊 Gráficos de Probabilidade Predita")
    for target in targets:
        fig_prob = px.histogram(y_pred, nbins=10, title=f"Distribuição de Probabilidade Predita - {target}")
        st.plotly_chart(fig_prob)

    # 📌 Gráficos de Coeficientes do Modelo
    st.subheader("📊 Gráficos de Coeficientes do Modelo")
    for target in targets:
        coef_df = pd.DataFrame({
            "Variável": features,
            "Coeficiente": models[target].coef_
        })

        fig_coef = px.bar(coef_df, x="Variável", y="Coeficiente", title=f"Coeficientes do Modelo - {target}")
        st.plotly_chart(fig_coef)
