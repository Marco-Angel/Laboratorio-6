import streamlit as st
import time
from game import MarioGame, Direction
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Mario Bros Threading Game",
    page_icon="🎮",
    layout="wide"
)

# Título
st.title("🎮 Mario Bros - Threading Game")
st.markdown("### Juego de plataformas con Threading, Mutex y Semáforos")
st.markdown("---")

# Inicializar el juego en session_state
if 'game' not in st.session_state:
    st.session_state.game = MarioGame(width=800, height=600)
    st.session_state.game_started = False

game = st.session_state.game

# Sidebar - Controles
with st.sidebar:
    st.header("🕹️ Controles")
    
    st.markdown("""
    **Movimiento:**
    - ⬅️ Izquierda
    - ➡️ Derecha  
    - ⬆️ Saltar
    
    **Tips:**
    - Puedes moverte mientras saltas
    - Mantén presionando dirección + salto
    - Salto más alto y movimiento más rápido
    """)
    
    st.markdown("---")
    
    # Botones de control mejorados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️", use_container_width=True, key="left"):
            if st.session_state.game_started:
                game.move_player(Direction.LEFT)
                time.sleep(0.15)
                game.stop_player()
    
    with col2:
        if st.button("⬆️", use_container_width=True, key="jump"):
            if st.session_state.game_started:
                game.jump()
    
    with col3:
        if st.button("➡️", use_container_width=True, key="right"):
            if st.session_state.game_started:
                game.move_player(Direction.RIGHT)
                time.sleep(0.15)
                game.stop_player()
    
    # Botones combinados para salto con dirección
    st.markdown("**Saltos direccionales:**")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("⬅️ + ⬆️", use_container_width=True, key="jump_left"):
            if st.session_state.game_started:
                game.move_player(Direction.LEFT)
                game.jump()
                time.sleep(0.15)
    
    with col_b:
        if st.button("➡️ + ⬆️", use_container_width=True, key="jump_right"):
            if st.session_state.game_started:
                game.move_player(Direction.RIGHT)
                game.jump()
                time.sleep(0.15)
    
    st.markdown("---")
    
    # Control del juego
    if not st.session_state.game_started:
        if st.button("🚀 INICIAR JUEGO", type="primary", use_container_width=True):
            game.start_game()
            st.session_state.game_started = True
            st.rerun()
    else:
        if st.button("🛑 DETENER JUEGO", type="secondary", use_container_width=True):
            game.stop_game()
            st.session_state.game_started = False
            st.rerun()
        
        if st.button("🔄 REINICIAR", use_container_width=True):
            game.stop_game()
            st.session_state.game = MarioGame(width=800, height=600)
            st.session_state.game_started = False
            st.rerun()
    
    st.markdown("---")
    
    # Información del Threading
    st.subheader("🧵 Threading Info")
    
    if st.session_state.game_started:
        state = game.get_game_state()
        st.info(f"""
        **Hilos activos:** {state['active_threads']}
        
        **Tipos de hilos:**
        - Physics Thread
        - {len(state['enemies'])} Enemy Threads
        - Collision Thread
        - Coin Animation Thread
        
        **Sincronización:**
        - 🔒 Mutex para score
        - 🔒 Mutex para game state
        - 🚦 Semáforo (max 5 enemigos)
        """)
    else:
        st.info("""
        **Hilos que se crearán:**
        - Physics Thread
        - 5 Enemy Threads
        - Collision Thread
        - Coin Animation Thread
        
        **Sincronización:**
        - 🔒 Mutex (Lock) para score
        - 🔒 Mutex para game state
        - 🚦 Semáforo (max 5 enemigos)
        """)

# Obtener estado del juego
state = game.get_game_state()

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Puntuación", state['score'])

with col2:
    st.metric("❤️ Vidas", state['player']['lives'])

with col3:
    st.metric("🧵 Hilos Activos", state['active_threads'])

with col4:
    st.metric("🪙 Monedas", len(state['coins']))

st.markdown("---")

# Canvas del juego
st.subheader("🎮 Pantalla del Juego")

if st.session_state.game_started:
    # Crear componentes visuales
    import streamlit.components.v1 as components
    
    # Generar HTML del juego
    player = state['player']
    
    # Construir HTML para todos los elementos
    platforms_html = ""
    for p in state['platforms']:
        platforms_html += f'<div style="position: absolute; left: {p["x"]}px; top: {p["y"]}px; width: {p["width"]}px; height: {p["height"]}px; background: linear-gradient(to bottom, #8B4513, #654321); border: 2px solid #000; border-radius: 5px;"></div>'
    
    enemies_html = ""
    for e in state['enemies']:
        enemies_html += f'<div style="position: absolute; left: {e["x"]}px; top: {e["y"]}px; width: {e["width"]}px; height: {e["height"]}px; background-color: #00FF00; border: 2px solid #006400; border-radius: 3px;"></div>'
    
    coins_html = ""
    for c in state['coins']:
        coins_html += f'<div style="position: absolute; left: {c["x"]}px; top: {c["y"]}px; width: {c["width"]}px; height: {c["height"]}px; background: radial-gradient(circle, #FFD700, #FFA500); border: 2px solid #FF8C00; border-radius: 50%;"></div>'
    
    game_over_html = ""
    if state['game_over']:
        game_over_html = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: red; font-size: 72px; font-weight: bold; text-shadow: 4px 4px 8px #000;">GAME OVER</div>'
    
    # HTML completo
    full_html = f"""
    <div style="width: 800px; height: 600px; position: relative; background: linear-gradient(to bottom, #87CEEB 0%, #E0F6FF 50%, #654321 100%); border: 5px solid #FFD700; border-radius: 10px; margin: 0 auto;">
        
        <!-- Jugador -->
        <div style="position: absolute; left: {player['x']}px; top: {player['y']}px; width: {player['width']}px; height: {player['height']}px; background-color: #FFD700; border: 2px solid #FF8C00; border-radius: 3px;"></div>
        
        {platforms_html}
        {enemies_html}
        {coins_html}
        
        <!-- HUD -->
        <div style="position: absolute; top: 10px; left: 10px; color: white; font-family: 'Courier New', monospace; font-weight: bold; text-shadow: 2px 2px 4px #000; font-size: 18px;">
            Puntuación: {state['score']}<br>
            Vidas: {"❤️ " * player['lives']}<br>
            Hilos activos: {state['active_threads']}
        </div>
        
        {game_over_html}
    </div>
    """
    
    # Renderizar con components
    components.html(full_html, height=650)
    
    # Auto-refresh
    if not state['game_over']:
        time.sleep(0.05)
        st.rerun()
    else:
        st.error("☠️ ¡GAME OVER! Has perdido todas tus vidas.")
        if st.button("🔄 Jugar de nuevo", key="restart_gameover"):
            game.stop_game()
            st.session_state.game = MarioGame(width=800, height=600)
            st.session_state.game_started = False
            st.rerun()

else:
    st.info("👆 Presiona '🚀 INICIAR JUEGO' en la barra lateral para comenzar")
    
    # Placeholder
    st.markdown("""
    <div style="width: 800px; height: 600px; background: linear-gradient(to bottom, #87CEEB, #E0F6FF); border: 5px solid #FFD700; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
        <h1 style="color: white; text-shadow: 3px 3px 6px #000; font-size: 48px;">🎮 Presiona INICIAR para jugar</h1>
    </div>
    """, unsafe_allow_html=True)

# Información técnica
st.markdown("---")
st.subheader("🔧 Implementación Técnica")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    ### 🧵 Threading
    - **Hilo de Física**: Aplica gravedad y movimiento
    - **Hilos de Enemigos**: 5 hilos (uno por enemigo)
    - **Hilo de Colisiones**: Detecta colisiones
    - **Hilo de Animación**: Efectos visuales
    
    ### 🔒 Secciones Críticas
    - **Score**: Protegido con `Lock()`
    - **Vidas**: Protegido con `Lock()`
    - Evita race conditions
    """)

with col_right:
    st.markdown("""
    ### 🔐 Mutex (Lock)
    ```python
    with self.score_lock:
        self.score += points
    ```
    
    ### 🚦 Semáforos
    ```python
    semaphore = Semaphore(5)
    semaphore.acquire()
    # ... código ...
    semaphore.release()
    ```
    """)

# Tabla de hilos
if st.session_state.game_started:
    st.markdown("---")
    st.subheader("📊 Estado de los Hilos")
    
    thread_data = []
    thread_data.append({'Hilo': 'Physics', 'Estado': '🟢 Activo', 'Función': 'Física del jugador'})
    thread_data.append({'Hilo': 'Collision', 'Estado': '🟢 Activo', 'Función': 'Detectar colisiones'})
    thread_data.append({'Hilo': 'Coins', 'Estado': '🟢 Activo', 'Función': 'Animar monedas'})
    
    for i in range(len(state['enemies'])):
        thread_data.append({
            'Hilo': f'Enemy-{i}',
            'Estado': '🟢 Activo',
            'Función': 'Mover enemigo'
        })
    
    df = pd.DataFrame(thread_data)
    st.dataframe(df, use_container_width=True, hide_index=True)