import streamlit as st
import cv2
import time
from hand_detector import HandGestureDetector, GestureType
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Detector de Gestos de Mano",
    page_icon="🖐️",
    layout="wide"
)

# Título
st.title("🖐️ Detector de Gestos de Mano con MediaPipe")
st.markdown("### Procesamiento en tiempo real con Threading, Mutex y Semáforos")
st.markdown("---")

# Inicializar detector en session_state
if 'detector' not in st.session_state:
    st.session_state.detector = None
    st.session_state.detector_running = False

# Sidebar - Controles
with st.sidebar:
    st.header("⚙️ Controles")
    
    # Control del detector
    if not st.session_state.detector_running:
        if st.button("🎥 INICIAR DETECTOR", type="primary", use_container_width=True):
            try:
                st.session_state.detector = HandGestureDetector(max_hands=2)
                st.session_state.detector.start(camera_id=0)
                st.session_state.detector_running = True
                st.success("✅ Detector iniciado")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        if st.button("🛑 DETENER DETECTOR", type="secondary", use_container_width=True):
            if st.session_state.detector:
                st.session_state.detector.stop()
            st.session_state.detector_running = False
            st.session_state.detector = None
            st.success("✅ Detector detenido")
            st.rerun()
    
    st.markdown("---")
    
    # Información de gestos detectables
    st.subheader("🎯 Gestos Detectables")
    st.markdown("""
    - 👍 **Pulgar Arriba**
    - 👎 **Pulgar Abajo**
    - ✌️ **Paz** (2 dedos)
    - ✊ **Puño** (mano cerrada)
    - 🖐️ **Palma Abierta** (5 dedos)
    - ☝️ **Apuntando** (1 dedo)
    - 👌 **OK** (círculo)
    """)
    
    st.markdown("---")
    
    # Información técnica
    st.subheader("🧵 Threading Info")
    
    if st.session_state.detector_running and st.session_state.detector:
        stats = st.session_state.detector.get_statistics()
        st.info(f"""
        **Hilos activos:** {stats['active_threads']}
        
        **Tipos de hilos:**
        - CaptureThread (Cámara)
        - ProcessThread (MediaPipe)
        - FPSThread (Cálculo FPS)
        - StatsThread (Estadísticas)
        
        **Sincronización:**
        - 🔒 Mutex para frames
        - 🔒 Mutex para gestos
        - 🔒 Mutex para estadísticas
        - 🚦 Semáforo para cámara
        """)
    else:
        st.info("""
        **Hilos a crear:**
        - CaptureThread
        - ProcessThread
        - FPSThread
        - StatsThread
        
        **Sincronización:**
        - 🔒 3 Mutex (Lock)
        - 🚦 1 Semáforo
        """)

# Contenido principal
if st.session_state.detector_running and st.session_state.detector:
    
    # Obtener estadísticas
    stats = st.session_state.detector.get_statistics()
    gestures = st.session_state.detector.get_current_gestures()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎥 FPS", f"{stats['fps']}")
    
    with col2:
        st.metric("🧵 Hilos Activos", stats['active_threads'])
    
    with col3:
        st.metric("📊 Detecciones Totales", stats['total_detections'])
    
    with col4:
        uptime_mins = int(stats['uptime'] // 60)
        uptime_secs = int(stats['uptime'] % 60)
        st.metric("⏱️ Tiempo Activo", f"{uptime_mins}m {uptime_secs}s")
    
    st.markdown("---")
    
    # Video en tiempo real
    col_video, col_info = st.columns([2, 1])
    
    with col_video:
        st.subheader("📹 Cámara en Vivo")
        video_placeholder = st.empty()
        
        # Obtener y mostrar frame
        frame = st.session_state.detector.get_current_frame()
        if frame is not None:
            # Convertir BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
        else:
            video_placeholder.info("⏳ Esperando frames de la cámara...")
    
    with col_info:
        st.subheader("🖐️ Gestos Detectados")
        
        if gestures:
            for i, hand in enumerate(gestures):
                with st.container():
                    st.markdown(f"""
                    **Mano {i+1}:** {hand.hand_type}  
                    **Gesto:** {hand.gesture.value}  
                    **Confianza:** {hand.confidence:.1%}
                    """)
                    st.progress(hand.confidence)
                    st.markdown("---")
        else:
            st.info("👋 Muestra tus manos a la cámara")
    
    # Gráficos de estadísticas
    st.markdown("---")
    st.subheader("📊 Estadísticas de Gestos")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Gráfico de barras
        gesture_data = {
            'Gesto': list(stats['gesture_count'].keys()),
            'Cantidad': list(stats['gesture_count'].values())
        }
        df_gestures = pd.DataFrame(gesture_data)
        
        # Filtrar solo gestos con detecciones
        df_gestures = df_gestures[df_gestures['Cantidad'] > 0]
        
        if not df_gestures.empty:
            fig_bar = px.bar(
                df_gestures,
                x='Gesto',
                y='Cantidad',
                title='Gestos Detectados (Total)',
                color='Cantidad',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("⏳ Esperando detecciones...")
    
    with col_chart2:
        # Gráfico de pastel
        if not df_gestures.empty:
            fig_pie = go.Figure(data=[go.Pie(
                labels=df_gestures['Gesto'],
                values=df_gestures['Cantidad'],
                hole=0.4
            )])
            fig_pie.update_layout(
                title='Distribución de Gestos',
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("⏳ Esperando detecciones...")
    
    # Tabla de hilos
    st.markdown("---")
    st.subheader("🧵 Estado de los Hilos")
    
    thread_data = {
        'Hilo': ['CaptureThread', 'ProcessThread', 'FPSThread', 'StatsThread'],
        'Estado': ['🟢 Activo'] * 4,
        'Función': [
            'Capturar frames de cámara',
            'Procesar con MediaPipe',
            'Calcular FPS',
            'Actualizar estadísticas'
        ]
    }
    df_threads = pd.DataFrame(thread_data)
    st.dataframe(df_threads, use_container_width=True, hide_index=True)
    
    # Información técnica
    st.markdown("---")
    st.subheader("🔧 Implementación Técnica")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        ### 🧵 Threading
        - **CaptureThread**: Captura frames a ~100 FPS
        - **ProcessThread**: Procesa con MediaPipe a ~30 FPS
        - **FPSThread**: Calcula frames por segundo
        - **StatsThread**: Actualiza estadísticas cada segundo
        
        ### 🔒 Secciones Críticas
        - **Frame compartido**: Protegido con `frame_lock`
        - **Gestos detectados**: Protegido con `gesture_lock`
        - **Estadísticas**: Protegido con `stats_lock`
        """)
    
    with col_right:
        st.markdown("""
        ### 🔐 Mutex (Lock)
        ```python
        with self.gesture_lock:
            self.current_gestures = detected
            self.gesture_count[gesture] += 1
        ```
        
        ### 🚦 Semáforo
        ```python
        camera_semaphore = Semaphore(1)
        # Solo un hilo accede a cámara
        camera_semaphore.acquire()
        # ... usar cámara ...
        camera_semaphore.release()
        ```
        """)
    
    # Auto-refresh
    time.sleep(0.05)
    st.rerun()

else:
    # Pantalla de inicio
    st.info("👆 Presiona '🎥 INICIAR DETECTOR' en la barra lateral para comenzar")
    
    st.markdown("""
    ## 🎯 ¿Cómo funciona?
    
    Este detector utiliza **MediaPipe** de Google para detectar manos en tiempo real y reconocer gestos.
    
    ### 🧵 **Threading Implementado:**
    
    1. **Hilo de Captura**: Lee frames de la cámara constantemente
    2. **Hilo de Procesamiento**: Analiza cada frame con MediaPipe
    3. **Hilo de FPS**: Calcula los frames por segundo
    4. **Hilo de Estadísticas**: Mantiene conteo de gestos detectados
    
    ### 🔒 **Sincronización:**
    
    - **Mutex (Lock)**: Protege datos compartidos entre hilos
    - **Semáforo**: Controla acceso exclusivo a la cámara
    - **Secciones Críticas**: Actualización segura de contadores
    
    ### 🖐️ **Gestos Reconocidos:**
    
    - Pulgar arriba/abajo
    - Señal de paz (✌️)
    - Puño cerrado
    - Palma abierta
    - Apuntando con el dedo
    - OK (👌)
    
    """)
    
    # Imagen de ejemplo
    st.image("https://via.placeholder.com/800x400/4A90E2/FFFFFF?text=Presiona+INICIAR+para+activar+la+c%C3%A1mara", 
             use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    🖐️ Powered by MediaPipe + OpenCV + Streamlit + Threading
</div>
""", unsafe_allow_html=True)