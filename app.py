import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sentiment_analyzer import SentimentAnalyzer, cargar_comentarios
import time

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Sentimientos",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("💬 Análisis de Sentimientos en Reseñas de Productos")
st.markdown("### Procesamiento paralelo con Threading en Python")
st.markdown("---")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selector de número de hilos
    num_threads = st.slider(
        "Número de hilos",
        min_value=1,
        max_value=10,
        value=4,
        help="Más hilos = procesamiento más rápido"
    )
    
    st.markdown("---")
    
    # Opción para subir archivo
    st.subheader("📁 Cargar comentarios")
    archivo_subido = st.file_uploader(
        "Sube un archivo .txt",
        type=['txt'],
        help="Un comentario por línea"
    )
    
    st.markdown("---")
    st.info("👨‍💻 **Desarrollado con:**\n- Python Threading\n- Streamlit\n- Plotly")

# Inicializar el analizador
@st.cache_resource
def obtener_analizador():
    return SentimentAnalyzer()

analyzer = obtener_analizador()

# Cargar comentarios
comentarios = []

if archivo_subido is not None:
    # Leer archivo subido
    contenido = archivo_subido.read().decode('utf-8')
    comentarios = [linea.strip() for linea in contenido.split('\n') if linea.strip()]
    st.success(f"✅ Archivo cargado: {len(comentarios)} comentarios encontrados")
else:
    # Cargar archivo por defecto
    comentarios = cargar_comentarios('comentarios.txt')
    if comentarios:
        st.info(f"📄 Usando archivo por defecto: {len(comentarios)} comentarios")
    else:
        st.warning("⚠️ No se encontró comentarios.txt. Por favor sube un archivo.")

# Botón para iniciar análisis
if st.button("🚀 Iniciar Análisis", type="primary", use_container_width=True):
    if not comentarios:
        st.error("❌ No hay comentarios para analizar")
    else:
        # Contenedor para progreso
        progress_container = st.empty()
        
        with progress_container.container():
            st.info(f"⏳ Procesando {len(comentarios)} comentarios con {num_threads} hilos...")
            progress_bar = st.progress(0)
            
            # Realizar análisis
            inicio = time.time()
            resultados = analyzer.analizar_lote(comentarios, num_threads=num_threads)
            fin = time.time()
            
            progress_bar.progress(100)
            tiempo_total = fin - inicio
        
        # Limpiar contenedor de progreso
        progress_container.empty()
        
        # Guardar resultados en session_state
        st.session_state['resultados'] = resultados
        st.session_state['tiempo_total'] = tiempo_total
        st.session_state['stats'] = analyzer.obtener_estadisticas(resultados)

# Mostrar resultados si existen
if 'resultados' in st.session_state:
    resultados = st.session_state['resultados']
    stats = st.session_state['stats']
    tiempo_total = st.session_state['tiempo_total']
    
    # Métricas principales
    st.markdown("## 📊 Resultados del Análisis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⏱️ Tiempo de procesamiento",
            value=f"{tiempo_total:.2f}s",
            delta=f"{num_threads} hilos"
        )
    
    with col2:
        st.metric(
            label="😊 Positivos",
            value=stats['positivos'],
            delta=f"{stats['porcentaje_positivos']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="😞 Negativos",
            value=stats['negativos'],
            delta=f"{stats['porcentaje_negativos']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="😐 Neutros",
            value=stats['neutros'],
            delta=f"{stats['porcentaje_neutros']:.1f}%"
        )
    
    st.markdown("---")
    
    # Gráficos
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Distribución de Sentimientos")
        
        # Gráfico de pastel
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Positivo', 'Negativo', 'Neutro'],
            values=[stats['positivos'], stats['negativos'], stats['neutros']],
            marker=dict(colors=['#00D26A', '#FF4B4B', '#CCCCCC']),
            hole=0.4,
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig_pie.update_layout(
            height=400,
            showlegend=True,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_right:
        st.subheader("📊 Comparación de Sentimientos")
        
        # Gráfico de barras
        df_stats = pd.DataFrame({
            'Sentimiento': ['Positivo', 'Negativo', 'Neutro'],
            'Cantidad': [stats['positivos'], stats['negativos'], stats['neutros']],
            'Color': ['#00D26A', '#FF4B4B', '#CCCCCC']
        })
        
        fig_bar = px.bar(
            df_stats,
            x='Sentimiento',
            y='Cantidad',
            color='Sentimiento',
            color_discrete_map={
                'Positivo': '#00D26A',
                'Negativo': '#FF4B4B',
                'Neutro': '#CCCCCC'
            },
            text='Cantidad'
        )
        
        fig_bar.update_layout(
            height=400,
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        
        fig_bar.update_traces(textposition='outside')
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tabla de resultados detallados
    st.markdown("---")
    st.subheader("📋 Comentarios Analizados")
    
    # Crear DataFrame
    df_resultados = pd.DataFrame(resultados)
    df_resultados['emoji'] = df_resultados['sentimiento'].map({
        'positivo': '😊',
        'negativo': '😞',
        'neutro': '😐'
    })
    
    # Filtro por sentimiento
    filtro = st.multiselect(
        "Filtrar por sentimiento:",
        ['positivo', 'negativo', 'neutro'],
        default=['positivo', 'negativo', 'neutro']
    )
    
    df_filtrado = df_resultados[df_resultados['sentimiento'].isin(filtro)]
    
    # Mostrar tabla con colores
    def colorear_fila(row):
        if row['sentimiento'] == 'positivo':
            return ['background-color: #E8F8F5'] * len(row)
        elif row['sentimiento'] == 'negativo':
            return ['background-color: #FADBD8'] * len(row)
        else:
            return ['background-color: #F4F6F7'] * len(row)
    
    st.dataframe(
        df_filtrado[['emoji', 'comentario', 'sentimiento', 'thread_id']].style.apply(colorear_fila, axis=1),
        use_container_width=True,
        height=400
    )
    
    # Botón de descarga
    csv = df_resultados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar resultados (CSV)",
        data=csv,
        file_name="analisis_sentimientos.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    # Mensaje inicial
    st.info("👆 Configura los parámetros en la barra lateral y haz clic en 'Iniciar Análisis' para comenzar")
    
    # Mostrar ejemplo de comentarios
    if comentarios:
        with st.expander("👁️ Ver comentarios cargados"):
            for i, comentario in enumerate(comentarios[:5], 1):
                st.text(f"{i}. {comentario}")
            if len(comentarios) > 5:
                st.text(f"... y {len(comentarios) - 5} comentarios más")