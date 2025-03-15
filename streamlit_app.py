import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="NBA Streamoku",
    page_icon="🏀",
    layout="wide"
)

# Estilo CSS inspirado en Sofascore
st.markdown("""
<style>
    .main-header {background-color: #132257; color: white; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;}
    .game-card {background-color: white; border-radius: 5px; padding: 1rem; margin: 0.5rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.12);}
    .team-logo {width: 30px; height: 30px; vertical-align: middle;}
    .live-indicator {color: #ff4747; font-weight: bold;}
    .score {font-size: 18px; font-weight: bold;}
    .team-name {margin-left: 10px; font-weight: bold;}
    .stat-card {background-color: #f8f9fa; border-radius: 5px; padding: 1rem; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'><h1>🏀 NBA Streamoku</h1></div>", unsafe_allow_html=True)

# URLs de los datos en tu repositorio de GitHub
GITHUB_BASE_URL = "https://raw.githubusercontent.com/Lperelli/nba-dashboard/main/nba_data"
TEAMS_URL = f"{GITHUB_BASE_URL}/teams.json"
PLAYERS_URL = f"{GITHUB_BASE_URL}/players.json"
RECENT_GAMES_URL = f"{GITHUB_BASE_URL}/recent_games.json"
TODAY_GAMES_URL = f"{GITHUB_BASE_URL}/today_games.json"
STANDINGS_URL = f"{GITHUB_BASE_URL}/standings.json"
TEAM_STATS_URL = f"{GITHUB_BASE_URL}/team_stats.json"

# Función para cargar datos desde GitHub
@st.cache_data(ttl=600)
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error cargando datos: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Pestañas principales
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏀 Partidos", "👥 Equipos", "📈 Estadísticas"])

# Pestaña 1: Dashboard principal
with tab1:
    st.header("Dashboard NBA")
    
    # Cargar datos básicos
    teams_data = load_data(TEAMS_URL)
    today_games_data = load_data(TODAY_GAMES_URL)
    
    if teams_data:
        # Mostrar algunos equipos
        st.subheader("Equipos NBA")
        
        # Convertir a DataFrame para mejor visualización
        teams_df = pd.DataFrame(teams_data)
        
        # Mostrar en dos columnas
        cols = st.columns(2)
        for i, col in enumerate(cols):
            with col:
                st.write(f"### Conferencia {'Este' if i==0 else 'Oeste'}")
                conf = 'East' if i==0 else 'West'
                conf_teams = teams_df[teams_df['conference'] == conf]
                st.dataframe(conf_teams[['full_name', 'city', 'abbreviation']], hide_index=True)
    
    # Mostrar partidos de hoy
    if today_games_data:
        st.subheader("Partidos de hoy")
        
        # Extraer partidos del JSON (depende de la estructura de tus datos)
        if 'scoreboard' in today_games_data and 'games' in today_games_data['scoreboard']:
            games = today_games_data['scoreboard']['games']
            
            for game in games[:5]:  # Mostrar hasta 5 partidos
                with st.container():
                    st.markdown(f"<div class='game-card'>", unsafe_allow_html=True)
                    
                    cols = st.columns([3, 1, 3])
                    
                    # Equipo visitante
                    with cols[0]:
                        st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.markdown(f"<span class='team-name'>{game['awayTeam']['teamTricode']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='score'>{game['awayTeam']['score']}</span>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Estado
                    with cols[1]:
                        st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.markdown(f"<span class='live-indicator'>{game['gameStatusText']}</span>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Equipo local
                    with cols[2]:
                        st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.markdown(f"<span class='team-name'>{game['homeTeam']['teamTricode']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='score'>{game['homeTeam']['score']}</span>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay partidos programados para hoy")

# Pestaña 2: Partidos
with tab2:
    st.header("Partidos NBA")
    
    # Cargar partidos recientes
    recent_games = load_data(RECENT_GAMES_URL)
    
    if recent_games:
        # Convertir a DataFrame
        games_df = pd.DataFrame(recent_games)
        
        # Formatear fecha
        if 'GAME_DATE' in games_df.columns:
            games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE']).dt.strftime('%Y-%m-%d')
        
        # Filtrar por equipo (opcional)
        if teams_data:
            teams_dict = {team['full_name']: team['id'] for team in teams_data}
            selected_team = st.selectbox("Filtrar por equipo:", ["Todos los equipos"] + list(teams_dict.keys()))
            
            if selected_team != "Todos los equipos":
                team_id = teams_dict[selected_team]
                games_df = games_df[games_df['TEAM_ID'] == team_id]
        
        # Mostrar partidos
        st.dataframe(
            games_df[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'FG_PCT']].head(20),
            hide_index=True,
            column_config={
                'GAME_DATE': 'Fecha',
                'MATCHUP': 'Partido',
                'WL': 'Resultado',
                'PTS': 'Puntos',
                'REB': 'Rebotes',
                'AST': 'Asistencias',
                'FG_PCT': '% Tiro'
            }
        )
    else:
        st.info("No se pudieron cargar los datos de partidos recientes")

# Pestaña 3: Equipos
with tab3:
    st.header("Equipos NBA")
    
    # Cargar datos de equipos
    teams_data = load_data(TEAMS_URL)
    team_stats = load_data(TEAM_STATS_URL)
    
    if teams_data:
        # Selector de equipos
        team_names = [team['full_name'] for team in teams_data]
        selected_team = st.selectbox("Selecciona un equipo:", team_names)
        
        # Mostrar información del equipo seleccionado
        team = next((t for t in teams_data if t['full_name'] == selected_team), None)
        
        if team:
            st.subheader(f"{team['full_name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
                st.write(f"**Ciudad:** {team['city']}")
                st.write(f"**Abreviatura:** {team['abbreviation']}")
                st.write(f"**Conferencia:** {team['conference']}")
                st.write(f"**División:** {team['division']}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Buscar estadísticas del equipo
            if team_stats:
                team_stat = next((t for t in team_stats if t.get('TEAM_ID') == team['id']), None)
                
                if team_stat:
                    with col2:
                        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
                        st.write(f"**Victorias:** {team_stat.get('WINS', 'N/A')}")
                        st.write(f"**Derrotas:** {team_stat.get('LOSSES', 'N/A')}")
                        st.write(f"**Puntos por partido:** {team_stat.get('PTS', 'N/A'):.1f}")
                        st.markdown("</div>", unsafe_allow_html=True)

# Pestaña 4: Estadísticas
with tab4:
    st.header("Estadísticas NBA")
    
    # Cargar datos de clasificación
    standings_data = load_data(STANDINGS_URL)
    
    if standings_data:
        # Convertir a DataFrame
        standings_df = pd.DataFrame(standings_data)
        
        # Pestañas para Este/Oeste
        conf_tab1, conf_tab2 = st.tabs(["Conferencia Este", "Conferencia Oeste"])
        
        with conf_tab1:
            east_df = standings_df[standings_df['Conference'] == 'East']
            if not east_df.empty:
                st.dataframe(
                    east_df[['TeamName', 'Record', 'WinPCT', 'RANK']].sort_values('RANK'),
                    hide_index=True,
                    column_config={
                        'TeamName': 'Equipo',
                        'Record': 'Balance',
                        'WinPCT': '% Victorias',
                        'RANK': 'Posición'
                    }
                )
        
        with conf_tab2:
            west_df = standings_df[standings_df['Conference'] == 'West']
            if not west_df.empty:
                st.dataframe(
                    west_df[['TeamName', 'Record', 'WinPCT', 'RANK']].sort_values('RANK'),
                    hide_index=True,
                    column_config={
                        'TeamName': 'Equipo',
                        'Record': 'Balance',
                        'WinPCT': '% Victorias',
                        'RANK': 'Posición'
                    }
                )
    else:
        st.info("No se pudieron cargar los datos de clasificación")

# Información de actualización
st.markdown("---")
st.write(f"Datos actualizados: {datetime.now().strftime('%Y-%m-%d')}")
st.write("Fuente: NBA API")
