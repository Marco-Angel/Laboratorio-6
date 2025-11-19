# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para OpenCV y procesamiento de imágenes
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libavcodec-extra \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto de la aplicación (ajusta según tu app)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app_gestos.py"]