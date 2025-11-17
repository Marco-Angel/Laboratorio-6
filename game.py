import threading
import time
import random
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

class Direction(Enum):
    """Direcciones de movimiento"""
    LEFT = -1
    RIGHT = 1
    UP = 2
    DOWN = -2

@dataclass
class GameObject:
    """Clase base para objetos del juego"""
    x: float
    y: float
    width: float
    height: float
    active: bool = True

@dataclass
class Player(GameObject):
    """Jugador (Mario)"""
    velocity_x: float = 0
    velocity_y: float = 0
    on_ground: bool = False
    lives: int = 3

@dataclass
class Enemy(GameObject):
    """Enemigo que se mueve"""
    velocity_x: float = 2
    direction: Direction = Direction.RIGHT

@dataclass
class Coin(GameObject):
    """Moneda para recolectar"""
    collected: bool = False

@dataclass
class Platform(GameObject):
    """Plataforma estática"""
    pass

class MarioGame:
    """
    Juego tipo Mario Bros con Threading
    Implementa: Hilos, Mutex (Lock), Semáforos, Secciones Críticas
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        # Dimensiones del juego
        self.width = width
        self.height = height
        
        # Física mejorada
        self.gravity = 0.4
        self.jump_force = -15
        self.player_speed = 7
        self.air_control = 0.8  # Control en el aire
        
        # Puntuación y vidas
        self.score = 0
        self.game_over = False
        self.running = False
        
        # SINCRONIZACIÓN CON THREADING
        self.score_lock = threading.Lock()  # MUTEX para proteger score
        self.game_state_lock = threading.Lock()  # MUTEX para estado del juego
        self.enemy_semaphore = threading.Semaphore(5)  # Máximo 5 enemigos activos
        
        # Objetos del juego
        self.player = Player(x=50, y=400, width=30, height=30)
        self.platforms: List[Platform] = []
        self.enemies: List[Enemy] = []
        self.coins: List[Coin] = []
        
        # Hilos activos
        self.threads: List[threading.Thread] = []
        
        # Inicializar nivel
        self._init_level()
    
    def _init_level(self):
        """Inicializar plataformas, enemigos y monedas"""
        # Plataformas
        self.platforms = [
            Platform(0, 550, 800, 50),  # Suelo
            Platform(100, 450, 150, 20),
            Platform(300, 380, 120, 20),
            Platform(500, 320, 150, 20),
            Platform(200, 250, 100, 20),
            Platform(450, 180, 120, 20),
        ]
        
        # Enemigos (se activan con semáforo)
        self.enemies = [
            Enemy(150, 420, 25, 25),
            Enemy(350, 350, 25, 25),
            Enemy(550, 290, 25, 25),
            Enemy(250, 220, 25, 25),
            Enemy(500, 150, 25, 25),
        ]
        
        # Monedas
        self.coins = [
            Coin(180, 410, 15, 15),
            Coin(240, 410, 15, 15),
            Coin(360, 340, 15, 15),
            Coin(420, 340, 15, 15),
            Coin(580, 280, 15, 15),
            Coin(280, 210, 15, 15),
            Coin(530, 140, 15, 15),
            Coin(590, 140, 15, 15),
        ]
    
    def start_game(self):
        """Iniciar el juego y todos los hilos"""
        self.running = True
        self.game_over = False
        
        # HILO 1: Física del jugador (gravedad, movimiento)
        physics_thread = threading.Thread(target=self._player_physics_loop, daemon=True, name="Physics")
        physics_thread.start()
        self.threads.append(physics_thread)
        
        # HILO 2: Movimiento de enemigos
        for i, enemy in enumerate(self.enemies):
            enemy_thread = threading.Thread(
                target=self._enemy_movement_loop, 
                args=(enemy,),
                daemon=True,
                name=f"Enemy-{i}"
            )
            enemy_thread.start()
            self.threads.append(enemy_thread)
        
        # HILO 3: Detección de colisiones
        collision_thread = threading.Thread(target=self._collision_detection_loop, daemon=True, name="Collision")
        collision_thread.start()
        self.threads.append(collision_thread)
        
        # HILO 4: Animación de monedas (opcional, para efecto visual)
        coin_thread = threading.Thread(target=self._coin_animation_loop, daemon=True, name="Coins")
        coin_thread.start()
        self.threads.append(coin_thread)
        
        print(f"🎮 Juego iniciado con {len(self.threads)} hilos activos")
    
    def stop_game(self):
        """Detener el juego"""
        self.running = False
        time.sleep(0.5)  # Esperar a que hilos terminen
        print("🛑 Juego detenido")
    
    # ============ HILOS DEL JUEGO ============
    
    def _player_physics_loop(self):
        """HILO: Física del jugador (gravedad y movimiento)"""
        while self.running:
            # Aplicar gravedad
            if not self.player.on_ground:
                self.player.velocity_y += self.gravity
            
            # Actualizar posición
            self.player.x += self.player.velocity_x
            self.player.y += self.player.velocity_y
            
            # Límites de pantalla
            self.player.x = max(0, min(self.player.x, self.width - self.player.width))
            
            # Verificar si está en el suelo
            self._check_platform_collision()
            
            # Caída mortal
            if self.player.y > self.height:
                self._lose_life()
            
            time.sleep(0.016)  # ~60 FPS
    
    def _enemy_movement_loop(self, enemy: Enemy):
        """HILO: Movimiento de un enemigo"""
        # Adquirir semáforo (máximo 5 enemigos activos)
        self.enemy_semaphore.acquire()
        
        try:
            while self.running and enemy.active:
                # Mover enemigo
                enemy.x += enemy.velocity_x * (1 if enemy.direction == Direction.RIGHT else -1)
                
                # Cambiar dirección en los bordes de la plataforma
                on_platform = False
                for platform in self.platforms:
                    if (platform.y - enemy.height - 5 < enemy.y < platform.y + 5 and
                        platform.x < enemy.x + enemy.width < platform.x + platform.width):
                        on_platform = True
                        break
                
                # Cambiar dirección si llega al borde
                if not on_platform or enemy.x <= 0 or enemy.x >= self.width - enemy.width:
                    enemy.direction = Direction.LEFT if enemy.direction == Direction.RIGHT else Direction.RIGHT
                
                time.sleep(0.03)  # Velocidad del enemigo
        finally:
            # Liberar semáforo al terminar
            self.enemy_semaphore.release()
    
    def _collision_detection_loop(self):
        """HILO: Detectar colisiones (jugador con enemigos y monedas)"""
        while self.running:
            # Colisión con enemigos
            for enemy in self.enemies:
                if enemy.active and self._check_collision(self.player, enemy):
                    self._lose_life()
                    enemy.active = False
            
            # Colisión con monedas (SECCIÓN CRÍTICA)
            for coin in self.coins:
                if not coin.collected and self._check_collision(self.player, coin):
                    coin.collected = True
                    self._add_score(10)  # SECCIÓN CRÍTICA protegida con LOCK
            
            time.sleep(0.02)
    
    def _coin_animation_loop(self):
        """HILO: Animación de monedas (efecto visual opcional)"""
        while self.running:
            # Aquí podrías agregar efectos de brillo o rotación
            time.sleep(0.1)
    
    # ============ SECCIONES CRÍTICAS ============
    
    def _add_score(self, points: int):
        """
        SECCIÓN CRÍTICA: Agregar puntos al score
        Protegida con MUTEX (Lock) para evitar race conditions
        """
        with self.score_lock:  # MUTEX
            self.score += points
            print(f"💰 +{points} puntos | Score total: {self.score}")
    
    def _lose_life(self):
        """
        SECCIÓN CRÍTICA: Perder una vida
        Protegida con MUTEX
        """
        with self.game_state_lock:  # MUTEX
            self.player.lives -= 1
            print(f"💔 Vida perdida | Vidas restantes: {self.player.lives}")
            
            if self.player.lives <= 0:
                self.game_over = True
                self.running = False
                print("☠️ GAME OVER")
            else:
                # Resetear posición del jugador
                self.player.x = 50
                self.player.y = 400
                self.player.velocity_x = 0
                self.player.velocity_y = 0
    
    # ============ DETECCIÓN DE COLISIONES ============
    
    def _check_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        """Verificar colisión entre dos objetos"""
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)
    
    def _check_platform_collision(self):
        """Verificar si el jugador está sobre una plataforma"""
        self.player.on_ground = False
        
        for platform in self.platforms:
            if (self.player.velocity_y >= 0 and
                self.player.x + self.player.width > platform.x and
                self.player.x < platform.x + platform.width and
                self.player.y + self.player.height >= platform.y and
                self.player.y + self.player.height <= platform.y + 20):
                
                self.player.y = platform.y - self.player.height
                self.player.velocity_y = 0
                self.player.on_ground = True
                break
    
    # ============ CONTROLES DEL JUGADOR ============
    
    def move_player(self, direction: Direction):
        """Mover el jugador (funciona también en el aire)"""
        speed = self.player_speed
        if not self.player.on_ground:
            speed *= self.air_control  # Movimiento más lento en el aire
        
        if direction == Direction.LEFT:
            self.player.velocity_x = -speed
        elif direction == Direction.RIGHT:
            self.player.velocity_x = speed
    
    def stop_player(self):
        """Detener movimiento horizontal del jugador"""
        self.player.velocity_x = 0
    
    def jump(self):
        """Hacer que el jugador salte"""
        if self.player.on_ground:
            self.player.velocity_y = self.jump_force
            self.player.on_ground = False
    
    # ============ OBTENER ESTADO DEL JUEGO ============
    
    def get_game_state(self) -> dict:
        """Obtener el estado actual del juego para renderizar"""
        with self.score_lock:
            return {
                'player': {
                    'x': self.player.x,
                    'y': self.player.y,
                    'width': self.player.width,
                    'height': self.player.height,
                    'lives': self.player.lives
                },
                'platforms': [
                    {'x': p.x, 'y': p.y, 'width': p.width, 'height': p.height}
                    for p in self.platforms
                ],
                'enemies': [
                    {'x': e.x, 'y': e.y, 'width': e.width, 'height': e.height}
                    for e in self.enemies if e.active
                ],
                'coins': [
                    {'x': c.x, 'y': c.y, 'width': c.width, 'height': c.height}
                    for c in self.coins if not c.collected
                ],
                'score': self.score,
                'active_threads': len([t for t in self.threads if t.is_alive()]),
                'game_over': self.game_over
            }


# Ejemplo de uso
if __name__ == "__main__":
    game = MarioGame()
    game.start_game()
    
    print("🎮 Juego iniciado. Presiona Ctrl+C para salir.")
    print("Estado del juego cada 2 segundos:")
    
    try:
        for _ in range(20):  # 40 segundos
            time.sleep(2)
            state = game.get_game_state()
            print(f"\n📊 Score: {state['score']} | Vidas: {state['player']['lives']} | Hilos activos: {state['active_threads']}")
            print(f"   Enemigos activos: {len(state['enemies'])} | Monedas restantes: {len(state['coins'])}")
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo juego...")
    finally:
        game.stop_game()