import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="NBA Dashboard",
    page_icon="🏀",
    layout="wide"
)

# Estilo inspirado en Sofascore
st.markdown("""
<style>
    .main-header {background-color: #132257; color: white; padding: 1rem; border-radius: 0.25rem; margin-bottom: 1rem;}
    .game-card {background-color: white; border-radius: 0.25rem; padding: 0.75rem; margin-bottom: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12);}
    .live-indicator {color: #ff4b4b; font-weight: bold;}
    .score {font-size: 1.2rem; font-weight: bold;}
    .team-name {font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>🏀 NBA Dashboard</h1></div>", unsafe_allow_html=True)

# URLs de los datos NBA (puedes reemplazarlos con tus propios archivos más adelante)
TEAMS_URL = "https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json"
PLAYERS_URL = "https://raw.githubusercontent.com/bttmly/nba/master/data/players.json"

# Función para obtener datos desde GitHub
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

# Cargar datos de equipos
teams_data = get_github_data(TEAMS_URL)
players_data = get_github_data(PLAYERS_URL)

# Generar algunos partidos simulados para demostración
def generate_games(teams, n=5):
    import random
    from datetime import datetime, timedelta
    
    games = []
    today = datetime.now()
    
    for i in range(n):
        # Seleccionar equipos aleatorios sin repetir
        team_indices = random.sample(range(len(teams)), 2)
        home_team = teams[team_indices[0]]
        away_team = teams[team_indices[1]]
        
        # Generar puntuaciones
        home_score = random.randint(90, 120)
        away_score = random.randint(90, 120)
        
        # Estado del partido (algunos en vivo, otros finalizados)
        status = "En vivo" if i < 2 else "Finalizado"
        period = random.randint(1, 4) if status == "En vivo" else 4
        
        games.append({
            "id": i,
            "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "home_team": home_team["teamName"],
            "home_abbreviation": home_team["abbreviation"],
            "home_score": home_score,
            "away_team": away_team["teamName"],
            "away_abbreviation": away_team["abbreviation"],
            "away_score": away_score,
            "status": status,
            "period": period
        })
    
    return games

# Navegación principal
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🏀 Partidos", "👥 Equipos"])

with tab1:
    st.header("NBA Dashboard")
    
    if teams_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Equipos NBA por Conferencia")
            
            # Crear un DataFrame con la información de equipos
            teams_df = pd.DataFrame(teams_data)
            
            # Contar equipos por conferencia
            if "conference" in teams_df.columns:
                conference_counts = teams_df["conference"].value_counts()
                fig = px.pie(
                    values=conference_counts.values,
                    names=conference_counts.index,
                    title="Equipos por Conferencia",
                    color_discrete_sequence=["#17408B", "#C9082A"]
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Backup si no hay datos de conferencia
                st.write(f"Total de equipos: {len(teams_df)}")
                st.dataframe(teams_df.head())
        
        with col2:
            st.subheader("Partidos Recientes")
            
            # Generar partidos simulados usando los equipos reales
            games = generate_games(teams_data)
            games_df = pd.DataFrame(games)
            
            fig = go.Figure()
            
            for i, game in games_df.iterrows():
                fig.add_trace(go.Bar(
                    x=[game['home_score']],
                    y=[f"{game['away_abbreviation']} @ {game['home_abbreviation']}"],
                    orientation='h',
                    name=game['home_team'],
                    marker_color='#17408B',
                    text=game['home_score'],
                    textposition='auto',
                    width=0.5,
                    offset=0
                ))
                
                fig.add_trace(go.Bar(
                    x=[game['away_score']],
                    y=[f"{game['away_abbreviation']} @ {game['home_abbreviation']}"],
                    orientation='h',
                    name=game['away_team'],
                    marker_color='#C9082A',
                    text=game['away_score'],
                    textposition='auto',
                    width=0.5,
                    offset=-0.5
                ))
            
            fig.update_layout(
                title="Resultados de Partidos",
                barmode='overlay',
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No se pudieron cargar los datos de equipos")

with tab2:
    st.header("Partidos")
    
    if teams_data:
        # Generar partidos simulados
        games = generate_games(teams_data, 10)
        
        # Mostrar partidos como tarjetas
        for game in games:
            with st.container():
                st.markdown(f"<div class='game-card'>", unsafe_allow_html=True)
                
                cols = st.columns([4, 1, 4])
                
                with cols[0]:
                    st.markdown(f"<span class='team-name'>{game['away_team']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='score'>{game['away_score']}</span>", unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"<span class='live-indicator'>{game['status']}</span>", unsafe_allow_html=True)
                    if game['status'] == "En vivo":
                        st.markdown(f"Periodo {game['period']}", unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"<span class='team-name'>{game['home_team']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='score'>{game['home_score']}</span>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("No se pudieron cargar los datos de equipos para mostrar partidos")

with tab3:
    st.header("Equipos NBA")
    
    if teams_data:
        # Crear DataFrame
        teams_df = pd.DataFrame(teams_data)
        
        # Mostrar tabla de equipos
        st.dataframe(teams_df, use_container_width=True)
        
        # Selector de equipo
        if "teamName" in teams_df.columns:
            team_names = teams_df["teamName"].tolist()
            selected_team = st.selectbox("Selecciona un equipo para ver detalles:", team_names)
            
            # Mostrar información del equipo seleccionado
            if selected_team:
                team_info = teams_df[teams_df["teamName"] == selected_team].iloc[0]
                
                st.subheader(f"Información de {selected_team}")
                
                # Mostrar datos disponibles
                for col in team_info.index:
                    if pd.notna(team_info[col]) and team_info[col] != "":
                        st.write(f"**{col}:** {team_info[col]}")
    else:
        st.error("No se pudieron cargar los datos de equipos")

# Footer
st.markdown("---")
st.write("Dashboard NBA - Usando datos de equipos reales y simulaciones de partidos")
st.write("Los datos se actualizarán para mostrar información en tiempo real cuando se implemente la versión completa")
