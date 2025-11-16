import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import time

class SentimentAnalyzer:
    """
    Analizador de sentimientos usando threading para procesamiento paralelo
    """
    
    def __init__(self):
        # Diccionario de palabras positivas y negativas
        self.palabras_positivas = {
            'excelente', 'increíble', 'perfecto', 'fantástico', 'bueno',
            'recomiendo', 'encanta', 'satisfecho', 'feliz', 'mejor',
            'rápida', 'potente', 'hermosas', 'vale', 'superó'
        }
        
        self.palabras_negativas = {
            'decepcionado', 'pésima', 'rompió', 'problemas', 'peor',
            'horrible', 'terrible', 'defectuoso', 'malo', 'no vale',
            'no funciona', 'no recomiendo'
        }
        
        # Lock para sincronización
        self.lock = threading.Lock()
        self.resultados = []
    
    def analizar_sentimiento(self, texto: str) -> str:
        """
        Analiza el sentimiento de un texto individual
        """
        texto = texto.lower()
        
        # Contar palabras positivas y negativas
        count_positivas = sum(1 for palabra in self.palabras_positivas if palabra in texto)
        count_negativas = sum(1 for palabra in self.palabras_negativas if palabra in texto)
        
        # Determinar sentimiento
        if count_positivas > count_negativas:
            return 'positivo'
        elif count_negativas > count_positivas:
            return 'negativo'
        else:
            return 'neutro'
    
    def procesar_comentario(self, comentario: str, indice: int) -> Dict:
        """
        Procesa un comentario individual (será ejecutado por cada hilo)
        """
        # Simular procesamiento (en la realidad podría ser análisis más complejo)
        time.sleep(0.1)
        
        sentimiento = self.analizar_sentimiento(comentario)
        
        resultado = {
            'indice': indice,
            'comentario': comentario,
            'sentimiento': sentimiento,
            'thread_id': threading.current_thread().name
        }
        
        # Usar lock para actualizar resultados de forma segura
        with self.lock:
            self.resultados.append(resultado)
        
        return resultado
    
    def analizar_lote(self, comentarios: List[str], num_threads: int = 4) -> List[Dict]:
        """
        Analiza un lote de comentarios usando ThreadPoolExecutor
        """
        self.resultados = []  # Limpiar resultados anteriores
        
        print(f"🚀 Iniciando análisis con {num_threads} hilos...")
        inicio = time.time()
        
        # Usar ThreadPoolExecutor para procesamiento paralelo
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Crear tareas para cada comentario
            futuros = [
                executor.submit(self.procesar_comentario, comentario, i)
                for i, comentario in enumerate(comentarios)
            ]
            
            # Esperar a que todas las tareas terminen
            for futuro in futuros:
                futuro.result()
        
        fin = time.time()
        tiempo_total = fin - inicio
        
        print(f"✅ Análisis completado en {tiempo_total:.2f} segundos")
        
        # Ordenar resultados por índice
        self.resultados.sort(key=lambda x: x['indice'])
        
        return self.resultados
    
    def obtener_estadisticas(self, resultados: List[Dict]) -> Dict:
        """
        Calcula estadísticas del análisis
        """
        total = len(resultados)
        positivos = sum(1 for r in resultados if r['sentimiento'] == 'positivo')
        negativos = sum(1 for r in resultados if r['sentimiento'] == 'negativo')
        neutros = sum(1 for r in resultados if r['sentimiento'] == 'neutro')
        
        return {
            'total': total,
            'positivos': positivos,
            'negativos': negativos,
            'neutros': neutros,
            'porcentaje_positivos': (positivos / total * 100) if total > 0 else 0,
            'porcentaje_negativos': (negativos / total * 100) if total > 0 else 0,
            'porcentaje_neutros': (neutros / total * 100) if total > 0 else 0
        }


# Función auxiliar para cargar comentarios desde archivo
def cargar_comentarios(ruta_archivo: str) -> List[str]:
    """
    Carga comentarios desde un archivo de texto
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            comentarios = [linea.strip() for linea in f if linea.strip()]
        return comentarios
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {ruta_archivo}")
        return []


# Ejemplo de uso
if __name__ == "__main__":
    # Cargar comentarios
    comentarios = cargar_comentarios('comentarios.txt')
    
    if comentarios:
        # Crear analizador
        analyzer = SentimentAnalyzer()
        
        # Analizar con 4 hilos
        resultados = analyzer.analizar_lote(comentarios, num_threads=4)
        
        # Mostrar resultados
        print("\n📊 RESULTADOS DEL ANÁLISIS:")
        print("-" * 80)
        for r in resultados:
            emoji = "😊" if r['sentimiento'] == 'positivo' else "😞" if r['sentimiento'] == 'negativo' else "😐"
            print(f"{emoji} [{r['sentimiento'].upper()}] {r['comentario'][:60]}...")
        
        # Mostrar estadísticas
        stats = analyzer.obtener_estadisticas(resultados)
        print("\n📈 ESTADÍSTICAS:")
        print(f"Total de comentarios: {stats['total']}")
        print(f"Positivos: {stats['positivos']} ({stats['porcentaje_positivos']:.1f}%)")
        print(f"Negativos: {stats['negativos']} ({stats['porcentaje_negativos']:.1f}%)")
        print(f"Neutros: {stats['neutros']} ({stats['porcentaje_neutros']:.1f}%)")
