# Laboratorio-6
---
##  Primer punto
---

###  PASO 1: Configuraci´on del Proyecto
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

---


### Paso 7:Ejecutar el proyecto con streamlit y Docker
#### Con streamlit
En esta parte de la actividad se crea un entorno virtual con el comando (python -m venv venv)
y luego con el comando (venv) se activa el entorno virtual para asi poder instalar las dependencias.
la imagen primera muestra que estás dentro de tu entorno virtual (venv) y ejecutaste la actualizacion de
pip, que ya estaba en su ultima versión. Luego se instalo streamlit, pandas y plotly: las dos primeras
ya estaban instaladas en el entorno, por eso aparece “Requirement already satisfied”, mientras que
plotly sí se descargó e instaló en ese momento. En resumen, todas las librerías necesarias quedaron
correctamente instaladas y no hubo errores.
<img width="916" height="277" alt="image" src="https://github.com/user-attachments/assets/2c35f4db-61c3-43fd-afbe-d50014575adb" />

 La segunda imagen muestra la ejecución de una aplicaci´on de Streamlit desde la terminal, donde el sistema
indica que el análisis se realizó con éxito y en poco tiempo. Sin embargo, el mensaje tambien resalta
repetidas advertencias sobre la futura eliminacion del par´ametro usecontainerwidth, recomendando
reemplazarlo por width antes del 31 de diciembre de 2025. Aunque la app funciona correctamente
y genera las URL de acceso local y en red, las advertencias indican que ser´a necesario actualizar el
codigo para evitar problemas de compatibilidad en versiones futuras.

<img width="802" height="630" alt="image" src="https://github.com/user-attachments/assets/59403ebb-1ccb-41b6-aa78-ac9366f8bd05" />
<img width="844" height="498" alt="image" src="https://github.com/user-attachments/assets/aa820cd1-0f1e-445d-8cfe-f7be38d74092" />

---

#### Con Docker
La imagen muestra el proceso exitoso de construcci´on y ejecuci´on de una imagen Docker para el
proyecto “proyecto-sentimientos”. Se observa c´omo Docker compila cada capa del Dockerfile, copia
los archivos necesarios, instala las dependencias desde requirements.txt y finalmente genera la imagen
sin errores. Luego, se ejecuta varias veces el comando docker run -p 8501:8501, indicando que se
est´a levantando un servicio (probablemente una aplicaci´on Streamlit) en el puerto 8501. En general, la
terminal refleja que el contenedor se construy´o correctamente y que la aplicaci´on est´a siendo desplegada
de manera local a trav´es de Docker.

<img width="600" height="601" alt="image" src="https://github.com/user-attachments/assets/109bf667-89da-45fc-835b-43cf2175dee6" />
<img width="600" height="276" alt="image" src="https://github.com/user-attachments/assets/691a4f2d-066b-4a1c-8487-6ae14584947e" />
<img width="832" height="309" alt="image" src="https://github.com/user-attachments/assets/d76832bf-6201-4dc6-b785-dff04f8fad9a" />

---

##  Segundo punto
---
#### Paso 1: Creacion de archivos
Como primero se creo un nuevo folder llamado **Juego-Mario-Bros**  en la imagense muestra la ejecucion de el comando ls, 
lo cual permitió visualizar los archivos que se crearon para la carpeta **Juego-Mario-Bros**. 
Ahora puedes ver las carpetas generadas por el entorno virtual (venv) y Python (pycache), además de los archivos de tu proyecto como game.py, appgame.py,
Dockerfile y requirements.txt, indicando que el directorio ya contiene todos los elementos necesarios para tu juego y su configuración.

<img width="779" height="426" alt="image" src="https://github.com/user-attachments/assets/f8c7dc5e-20e2-4855-812f-b74cc5a6a39d" />

---
#### Paso 2: Entorno virtual

<img width="716" height="65" alt="image" src="https://github.com/user-attachments/assets/9804644d-ea4f-4eda-a96c-1f74657c5eec" />

En la figura anterior se ve el proceso para preparar y usar un entorno virtual de Python. Primero
ejecutar python -m venv venv, lo que creó un entorno virtual llamado venv. Luego se activo ese
entorno con venv, lo cual se nota porque ahora aparece (venv) al inicio de la linea de comandos. Por
último, ejecutaste pip install -r requirements.txt para instalar automáticamente todas las dependencias
necesarias para tu proyecto según el archivo requirements.txt.

---
#### Paso 3: Prueba con streamlit
<img width="489" height="26" alt="image" src="https://github.com/user-attachments/assets/4f713328-47d9-4335-952c-aa0494de7497" />

En esta parte del proceso decidi primero hacerlo directamente con streamlit y rectificar que los codigos de los archivos estuvieran bien,
también verificar que el programa corriera sin ningun problema. Ahora explicando de lo que se hizo en la imagen despuesde de aver descargado el pip se se instalo con el comando ("pip install streamlit pandas plotly") para que se pueda ejecutar el programa con ("streamlit run app_game.py") y poder visualizar y ejecutar el juego

---

#### Paso 4: Iniciarlo con docker
<img width="641" height="355" alt="image" src="https://github.com/user-attachments/assets/84711324-6166-444c-b1c6-cf323924aba3" />
<img width="800" height="682" alt="image" src="https://github.com/user-attachments/assets/f639914e-2508-4e6b-9232-5382370dd601" />
<img width="664" height="330" alt="image" src="https://github.com/user-attachments/assets/e5cd977d-435b-45f4-b116-8c4e5d77c1b7" />


En estas imagenes se muestra cómo se construyo y se ejecuto la  aplicación dentro de Docker. Primero ejecute docker build -t juego-mario-bros .
lo que creó una imagen de Docker usando el Dockerfile de tu proyecto; durante el proceso se copiaron los archivos, se instaló Python 3.11, 
se agregó el código de tu app y se instalaron las dependencias del archivo requirements.txt. 
Luego se corre el contenedor con docker run --name mario-game -p 8501:8501 juego-mario-bros, exponiendo el puerto 8501 para poder acceder
a la aplicación Streamlit desde tu navegador. Finalmente, Docker dejó listo el enlace para abrir la app: http://0.0.0.0:8501.

---

#### Paso 5: Jugar

<img width="637" height="345" alt="image" src="https://github.com/user-attachments/assets/a09ff2b1-2648-4ad8-b39f-f37afc7a54ed" />

En esta imagen se muestra la interfaz de tu juego corriendo dentro de la aplicación web creada con Streamlit. A la izquierda aparecen los controles y opciones del jugador, como los botones para moverse, saltar, detener el juego o reiniciarlo, además de algunos tips para jugar. A la derecha se encuentra la “Pantalla del Juego”, donde se visualizan los elementos principales: el personaje, las plataformas, las monedas y los indicadores de estado como la puntuación, las vidas y la cantidad de hilos activos. En conjunto, la imagen muestra que el juego ya está funcionando correctamente dentro de la interfaz web.


<img width="800" height="723" alt="image" src="https://github.com/user-attachments/assets/d9f404f9-f6eb-4709-8ec4-2af5920e136d" />

En esta imagen se muestra el momento en que el jugador pierde la partida dentro del juego. En la parte superior izquierda aparecen los indicadores finales: una puntuación de 40, vidas en 0 y hilos activos en 0, lo que significa que el personaje ya no puede continuar. En el centro de la pantalla se despliega un gran mensaje rojo de “GAME OVER”, indicando claramente que el juego ha terminado. Al fondo se mantienen las plataformas, monedas y el personaje, mostrando el escenario justo en el instante en que ocurrió la derrota.


<img width="1326" height="838" alt="image" src="https://github.com/user-attachments/assets/ff9c8eb8-ef13-4067-969e-041b78d4ee49" />

En esta imagen se muestra la sección de implementación técnica del proyecto, donde se explica cómo funciona internamente el juego utilizando multihilos y mecanismos de sincronización. A la izquierda aparece el listado de hilos que maneja el sistema —como el hilo de física, de enemigos, colisiones y animación— junto con las secciones críticas protegidas por cerrojos (Locks) para evitar condiciones de carrera al modificar la puntuación y las vidas. A la derecha se ilustran los conceptos de Mutex (Lock) y Semáforos, con fragmentos de código que muestran cómo se aplican para controlar el acceso a recursos compartidos. Finalmente, en la parte inferior se presenta una tabla que muestra el estado actual de los hilos del juego y la función que cumple cada uno, evidenciando la arquitectura concurrente que hace posible el funcionamiento del juego.

---
## Tercer punto

---
### Paso 1: Carpeta y archivos
El tercer punto se concentra en la detecion de gestos con las manos, para ello se creo una carpeta llamada **Proycto-Gestos** y dentro de ella se crean los siguientes archivos que se evidencian en la siguiente imagen, donde en cada uno se le debe hacer la respectiva codificación para construir el objetivo de este punto para asi poder ejecutarlo en terminal y llevarlo a cabo.

<img width="689" height="253" alt="image" src="https://github.com/user-attachments/assets/528acafc-e14b-4dd4-857f-3a1b15edc1ec" />


<img width="800" height="570" alt="image" src="https://github.com/user-attachments/assets/86ae4585-8a22-47a8-9503-625f45c41d06" />

<img width="953" height="73" alt="image" src="https://github.com/user-attachments/assets/53c0f837-2d0a-4985-88da-97c118ff893e" />


<img width="783" height="911" alt="image" src="https://github.com/user-attachments/assets/abbe429f-36c0-4b0f-b869-9b1f28178e3f" />

<img width="800" height="374" alt="image" src="https://github.com/user-attachments/assets/6013db17-37d2-4f29-922e-35210bd7ab21" />

<img width="988" height="577" alt="image" src="https://github.com/user-attachments/assets/223bafe6-66bb-4a3b-8d57-1d894799e6f8" />

<img width="804" height="598" alt="image" src="https://github.com/user-attachments/assets/a3a94e01-5baf-4285-9565-aa22c7d24d41" />

<img width="990" height="606" alt="image" src="https://github.com/user-attachments/assets/c3ff0970-3395-4063-a715-a62563cbb47d" />

<img width="1010" height="569" alt="image" src="https://github.com/user-attachments/assets/fddcb383-5d90-443e-b260-592c5ea73ee4" />


