import cv2
import mediapipe as mp
import threading
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

class GestureType(Enum):
    """Tipos de gestos detectables"""
    THUMBS_UP = "👍 Pulgar Arriba"
    THUMBS_DOWN = "👎 Pulgar Abajo"
    PEACE = "✌️ Paz"
    FIST = "✊ Puño"
    OPEN_PALM = "🖐️ Palma Abierta"
    POINTING = "☝️ Apuntando"
    OK = "👌 OK"
    UNKNOWN = "❓ Desconocido"

@dataclass
class HandData:
    """Datos de una mano detectada"""
    gesture: GestureType
    landmarks: List[Tuple[float, float]]
    hand_type: str  # "Left" o "Right"
    confidence: float

class HandGestureDetector:
    """
    Detector de gestos de mano usando MediaPipe y Threading
    Implementa: Hilos, Mutex, Semáforos, Secciones Críticas
    """
    
    def __init__(self, max_hands: int = 2):
        # MediaPipe configuración
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Detector de manos
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Control de cámara
        self.cap = None
        self.running = False
        self.frame = None
        self.processed_frame = None
        
        # Datos compartidos (protegidos con mutex)
        self.current_gestures: List[HandData] = []
        self.gesture_count: Dict[str, int] = {gesture.value: 0 for gesture in GestureType}
        self.fps = 0
        
        # SINCRONIZACIÓN CON THREADING
        self.frame_lock = threading.Lock()  # MUTEX para el frame
        self.gesture_lock = threading.Lock()  # MUTEX para gestos detectados
        self.stats_lock = threading.Lock()  # MUTEX para estadísticas
        self.camera_semaphore = threading.Semaphore(1)  # Solo un hilo accede a cámara
        
        # Hilos
        self.threads: List[threading.Thread] = []
        
        # Estadísticas
        self.total_detections = 0
        self.start_time = time.time()
    
    def start(self, camera_id: int = 0):
        """Iniciar detector y todos los hilos"""
        print("🎥 Iniciando cámara...")
        
        # Adquirir semáforo de cámara
        self.camera_semaphore.acquire()
        
        try:
            self.cap = cv2.VideoCapture(camera_id)
            if not self.cap.isOpened():
                raise Exception("No se pudo abrir la cámara")
            
            self.running = True
            
            # HILO 1: Captura de frames
            capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True,
                name="CaptureThread"
            )
            capture_thread.start()
            self.threads.append(capture_thread)
            
            # HILO 2: Procesamiento de gestos
            process_thread = threading.Thread(
                target=self._process_loop,
                daemon=True,
                name="ProcessThread"
            )
            process_thread.start()
            self.threads.append(process_thread)
            
            # HILO 3: Cálculo de FPS
            fps_thread = threading.Thread(
                target=self._fps_loop,
                daemon=True,
                name="FPSThread"
            )
            fps_thread.start()
            self.threads.append(fps_thread)
            
            # HILO 4: Actualización de estadísticas
            stats_thread = threading.Thread(
                target=self._stats_loop,
                daemon=True,
                name="StatsThread"
            )
            stats_thread.start()
            self.threads.append(stats_thread)
            
            print(f"✅ Detector iniciado con {len(self.threads)} hilos activos")
            
        except Exception as e:
            self.camera_semaphore.release()
            raise e
    
    def stop(self):
        """Detener detector y liberar recursos"""
        print("🛑 Deteniendo detector...")
        self.running = False
        
        time.sleep(0.5)  # Esperar a que hilos terminen
        
        if self.cap:
            self.cap.release()
        
        self.camera_semaphore.release()
        print("✅ Detector detenido")
    
    # ============ HILOS DEL DETECTOR ============
    
    def _capture_loop(self):
        """HILO 1: Capturar frames de la cámara"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # SECCIÓN CRÍTICA: Actualizar frame compartido
                with self.frame_lock:
                    self.frame = frame.copy()
            
            time.sleep(0.01)  # ~100 FPS máximo
    
    def _process_loop(self):
        """HILO 2: Procesar frames y detectar gestos"""
        while self.running:
            # Obtener frame actual
            with self.frame_lock:
                if self.frame is None:
                    time.sleep(0.1)
                    continue
                frame = self.frame.copy()
            
            # Convertir BGR a RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Procesar con MediaPipe
            results = self.hands.process(rgb_frame)
            
            # Dibujar anotaciones
            annotated_frame = frame.copy()
            detected_gestures = []
            
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Dibujar landmarks
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Detectar gesto
                    hand_type = results.multi_handedness[idx].classification[0].label
                    gesture = self._detect_gesture(hand_landmarks, hand_type)
                    confidence = results.multi_handedness[idx].classification[0].score
                    
                    # Extraer landmarks
                    landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                    
                    # Crear HandData
                    hand_data = HandData(
                        gesture=gesture,
                        landmarks=landmarks,
                        hand_type=hand_type,
                        confidence=confidence
                    )
                    detected_gestures.append(hand_data)
                    
                    # Dibujar texto del gesto
                    cv2.putText(
                        annotated_frame,
                        f"{hand_type}: {gesture.value}",
                        (10, 30 + idx * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
            
            # SECCIÓN CRÍTICA: Actualizar gestos detectados
            with self.gesture_lock:
                self.current_gestures = detected_gestures
                self.processed_frame = annotated_frame
                
                # Actualizar contador de gestos
                for hand_data in detected_gestures:
                    self.gesture_count[hand_data.gesture.value] += 1
                    self.total_detections += 1
            
            time.sleep(0.03)  # ~30 FPS de procesamiento
    
    def _fps_loop(self):
        """HILO 3: Calcular FPS"""
        last_time = time.time()
        frame_count = 0
        
        while self.running:
            current_time = time.time()
            frame_count += 1
            
            if current_time - last_time >= 1.0:
                # SECCIÓN CRÍTICA: Actualizar FPS
                with self.stats_lock:
                    self.fps = frame_count
                
                frame_count = 0
                last_time = current_time
            
            time.sleep(0.1)
    
    def _stats_loop(self):
        """HILO 4: Actualizar estadísticas periódicamente"""
        while self.running:
            with self.stats_lock:
                elapsed_time = time.time() - self.start_time
                # Aquí podrían agregarse más estadísticas
            
            time.sleep(1)
    
    # ============ DETECCIÓN DE GESTOS ============
    
    def _detect_gesture(self, hand_landmarks, hand_type: str) -> GestureType:
        """
        Detectar el gesto basado en los landmarks de la mano
        Algoritmo simplificado basado en posiciones relativas de dedos
        """
        # Extraer coordenadas importantes
        landmarks = hand_landmarks.landmark
        
        # Puntas de los dedos
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Bases de los dedos
        thumb_ip = landmarks[3]
        index_pip = landmarks[6]
        middle_pip = landmarks[10]
        ring_pip = landmarks[14]
        pinky_pip = landmarks[18]
        
        # Palma
        wrist = landmarks[0]
        
        # Contar dedos extendidos
        fingers_up = []
        
        # Pulgar (diferente para mano izquierda y derecha)
        if hand_type == "Right":
            fingers_up.append(thumb_tip.x < thumb_ip.x)
        else:
            fingers_up.append(thumb_tip.x > thumb_ip.x)
        
        # Otros dedos
        fingers_up.append(index_tip.y < index_pip.y)
        fingers_up.append(middle_tip.y < middle_pip.y)
        fingers_up.append(ring_tip.y < ring_pip.y)
        fingers_up.append(pinky_tip.y < pinky_pip.y)
        
        fingers_count = sum(fingers_up)
        
        # Identificar gesto
        if fingers_count == 0:
            return GestureType.FIST
        
        elif fingers_count == 5:
            return GestureType.OPEN_PALM
        
        elif fingers_count == 1 and fingers_up[0]:  # Solo pulgar
            # Verificar si está arriba o abajo
            if thumb_tip.y < wrist.y:
                return GestureType.THUMBS_UP
            else:
                return GestureType.THUMBS_DOWN
        
        elif fingers_count == 1 and fingers_up[1]:  # Solo índice
            return GestureType.POINTING
        
        elif fingers_count == 2 and fingers_up[1] and fingers_up[2]:  # Índice y medio
            return GestureType.PEACE
        
        elif fingers_count == 3 and fingers_up[0] and fingers_up[1] and fingers_up[2]:
            # Pulgar, índice y medio formando círculo
            return GestureType.OK
        
        else:
            return GestureType.UNKNOWN
    
    # ============ OBTENER DATOS ============
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Obtener frame procesado actual"""
        with self.gesture_lock:
            return self.processed_frame.copy() if self.processed_frame is not None else None
    
    def get_current_gestures(self) -> List[HandData]:
        """Obtener gestos detectados actualmente"""
        with self.gesture_lock:
            return self.current_gestures.copy()
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas del detector"""
        with self.stats_lock:
            with self.gesture_lock:
                return {
                    'fps': self.fps,
                    'total_detections': self.total_detections,
                    'gesture_count': self.gesture_count.copy(),
                    'active_threads': len([t for t in self.threads if t.is_alive()]),
                    'uptime': time.time() - self.start_time
                }


# Ejemplo de uso
if __name__ == "__main__":
    detector = HandGestureDetector(max_hands=2)
    
    try:
        detector.start(camera_id=0)
        print("✅ Detector corriendo. Presiona Ctrl+C para salir.")
        print("📊 Mostrando estadísticas cada 3 segundos...")
        
        while True:
            time.sleep(3)
            
            stats = detector.get_statistics()
            gestures = detector.get_current_gestures()
            
            print(f"\n📊 FPS: {stats['fps']} | Hilos: {stats['active_threads']} | Detecciones: {stats['total_detections']}")
            
            if gestures:
                for i, hand in enumerate(gestures):
                    print(f"   Mano {i+1} ({hand.hand_type}): {hand.gesture.value} ({hand.confidence:.2f})")
            else:
                print("   No se detectaron manos")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo...")
    finally:
        detector.stop()

