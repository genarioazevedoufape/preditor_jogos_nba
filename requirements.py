# requirements.py
import os

# Definir as bibliotecas necessárias
libraries = [
    "streamlit",
    "pandas",
    "plotly_express==0.4.0",
    "nba_api",
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "numpy",
    "scipy",
    
]

# Instalar as bibliotecas
for library in libraries:
    os.system(f"pip install {library}")
