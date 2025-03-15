import streamlit as st
import pandas as pd
import requests

st.title("🏀 NBA Dashboard Minimalista")

# URL simple para probar la conexión
TEAMS_URL = "https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json"

# Función para obtener datos
@st.cache_data(ttl=600)
def get_github_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error al obtener datos: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Mostrar mensaje de carga
st.write("Cargando datos de equipos NBA...")

# Cargar datos de equipos
teams_data = get_github_data(TEAMS_URL)

if teams_data:
    st.success(f"✅ Se cargaron datos de {len(teams_data)} equipos NBA")
    
    # Convertir a DataFrame
    teams_df = pd.DataFrame(teams_data)
    
    # Mostrar tabla de equipos
    st.write("### Equipos NBA")
    st.dataframe(teams_df)
    
    # Mostrar algunos equipos individualmente
    st.write("### Detalles de equipos")
    for i, team in enumerate(teams_data[:5]):
        st.write(f"**{team.get('teamName', 'N/A')}**")
        st.write(f"Abreviatura: {team.get('abbreviation', 'N/A')}")
        st.write(f"Ciudad: {team.get('location', 'N/A')}")
        st.write("---")
else:
    st.error("❌ No se pudieron cargar los datos de equipos")
