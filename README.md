# Laboratorio-6
---
##  Primer punto
---

### 1.1 PASO 1: Configuraci´on del Proyecto
Se crea una nueva carpeta llamada ”Proyecto-sentimientos”, para despues crear cuatro archivos como
se muestra en la siguiente imagen.

<img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/e0bea35c-0503-415e-be0a-b77c06d897ac" />

El ideal para cumplir con el primer punto es asignarle a cada archivo cierto codigo correspondiente
para lograr proceso bien estructurado dandole utilidad y protagonismo a cada uno de los archivos que
se crearon en este folder.

---
###  Paso 2: archivo de datos
<img width="799" height="463" alt="image" src="https://github.com/user-attachments/assets/d725a8ca-7f64-4fc6-8891-77934ac5e1d6" />

- En este parte del desarrollo se se escoge el archivo ”comentarios.txt” se implemeto comentarios con
sentido de diferentes resultados, ya siendo positivos, negativos y neutros para que se puedan cargar a
la hora de hacer la interfaz en streamlit.
---
### Paso 3: Analisis de Sentimientos con Threading
<img width="764" height="690" alt="image" src="https://github.com/user-attachments/assets/23cd23a0-90a9-46db-be8e-b8ee80d49bf5" />

- El codigo implementa un analizador de sentimientos que procesa m´ultiples comentarios simult´aneamente
usando threading. La clase SentimentAnalyzer contiene diccionarios de palabras positivas y negativas
que usa como referencia para clasificar cada texto.
- El metodo principal analizarlote utiliza ThreadPoolExecutor para crear m´ultiples hilos (4 por
defecto) que procesan comentarios en paralelo en lugar de uno por uno. Cada hilo ejecuta procesarcomentario, que analiza el texto contando palabras positivas/negativas y determina si el sentimiento es
positivo, negativo o neutro.
- Para evitar condiciones de carrera (cuando dos hilos intentan modificar la lista de resultados al
mismo tiempo), se usa threading.Lock como mecanismo de sincronizacion. El with self.lock: garantiza
que solo un hilo a la vez pueda agregar resultados a la lista compartida, previniendo p´erdida de
datos. Ventaja principal: Si procesar 15 comentarios toma 1.5 segundos de forma secuencial, con 4
hilos trabajando en paralelo se reduce a aproximadamente 0.4 segundos (casi 4 veces más rápido). El
método obtenerestadisticas calcula porcentajes de cada tipo de sentimiento para visualizaci´on posterior
en Streamlit.

---
###  PASO 4: Crear la aplicación Streamlit
<img width="673" height="685" alt="image" src="https://github.com/user-attachments/assets/ac490921-affc-4a25-8448-cf21fd34aaf5" />

El archivo app.py crea una aplicaci´on web interactiva usando Streamlit que permite visualizar el
analisis de sentimientos en tiempo real. La aplicación tiene una barra lateral (sidebar) donde el usuario
puede ajustar el número de hilos (1-10) mediante un slider y subir archivos .txt personalizados con
comentarios. La interfaz principal muestra m´etricas en tiempo real usando st.metric que despliegan
el tiempo de procesamiento, cantidad de sentimientos positivos/negativos/neutros con sus porcentajes.
Al presionar el bot´on ”Iniciar Analisis”, se ejecuta analyzer.analizarlote con el numero de hilos
configurado, mostrando una barra de progreso (st.progress) durante el procesamiento. Los resultados
se visualizan con dos gr´aficos interactivos de Plotly: un gr´afico de pastel (pie chart) que muestra la
distribucion porcentual de sentimientos con colores distintivos (verde para positivo, rojo para negativo, gris para neutro),
y un grafico de barras que compara las cantidades absolutas. Estos graficos
son dinamicos e interactivos (puedes hacer hover para ver detalles). La aplicacion incluye una tabla
filtrable con st.dataframe que muestra todos los comentarios analizados con colores de fondo segun
su sentimiento (verde claro para positivos, rojo claro para negativos). Los usuarios pueden filtrar por
tipo de sentimiento usando st.multiselect y descargar los resultados en CSV con st.downloadbutton.

---
###  PASO 5: Crear requirements.txt
<img width="648" height="263" alt="image" src="https://github.com/user-attachments/assets/106b4cfe-edef-4515-a32e-7f1b7133a436" />

El archivo requirements.txt especifica las bibliotecas Python necesarias para ejecutar el proyecto con
sus versiones exactas. Contiene tres dependencias principales: Streamlit 1.29.0 (framework para crear
la interfaz web), Pandas 2.1.4 (manipulaci´on y estructuraci´on de datos en tablas), y Plotly 5.18.0 (generacion de graficos interactivos). 
Este archivo permite instalar todas las dependencias automáticamente
con un solo comando: pip install -r requirements.txt, garantizando que todos usen las mismas versiones
de las bibliotecas. Es esencial para la reproducibilidad del proyecto y para que Docker construya la
imagen correctamente, ya que el Dockerfile lo utiliza durante el proceso de build. Puntos clave: Gesti´on
de dependencias, control de versiones, reproducibilidad del entorno, y preparaci´on para deployment en
Docker.

---
### Paso 6: crear Dockerfile
<img width="803" height="364" alt="image" src="https://github.com/user-attachments/assets/660e5896-8806-4bdd-8c12-3b07b4b12cf4" />

El Dockerfile define las instrucciones para crear una imagen Docker que empaqueta la aplicacion
con todas sus dependencias en un contenedor portable. Comienza con FROM python:3.11-slim, que
usa una imagen base ligera de Python 3.11 para minimizar el tama˜no final. El comando WORKDIR
/app establece el directorio de trabajo dentro del contenedor. Luego COPY requirements.txt . y RUN
pip install –no-cache-dir -r requirements.txt copian e instalan las dependencias antes de copiar el c´odigo
(aprovechando el cach´e de Docker para builds más rapidos). El COPY . . copia todos los archivos
del proyecto al contenedor. El EXPOSE 8501 documenta que la aplicaci´on usa el puerto 8501 (puerto
por defecto de Streamlit), aunque no lo abre automaticamente. Finalmente, CMD [”streamlit”, ”run”,
”app.py”, ...] define el comando que se ejecuta al iniciar el contenedor, lanzando la aplicaci´on Streamlit
accesible desde cualquier IP (–server.address=0.0.0.0).


