import pygame
import sys
import os
import math
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Приключения Василия - Финальная версия (F11 - полноэкранный режим)")

# Загрузка изображений
def load_image(filename, scale=1):
    """Загружает изображение и масштабирует его"""
    try:
        image = pygame.image.load(filename)
        if scale != 1:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (width, height))
        return image
    except Exception as e:
        print(f"Ошибка загрузки {filename}: {e}")
        return None

# Загружаем ассеты с правильными масштабами
background_far = load_image("assets/background/background_layer_far.png", 1.0)

# Персонаж 20% по высоте экрана
hero_no_sword_sprite = load_image("assets/characters/hero_no_sword.png", SCREEN_HEIGHT * 0.20 / 460)
hero_with_sword_sprite = load_image("assets/characters/hero_with_sword.png", SCREEN_HEIGHT * 0.20 / 460)
hero_attack_sprite = load_image("assets/characters/hero_attack.png", SCREEN_HEIGHT * 0.20 / 460)

# Объекты 15% по высоте экрана
sword_sprite = load_image("assets/objects/sword_in_stone.png", SCREEN_HEIGHT * 0.15 / 180)
crystal_1_sprite = load_image("assets/objects/crystals_1.png", SCREEN_HEIGHT * 0.15 / 280)
crystal_2_sprite = load_image("assets/objects/crystals_2.png", SCREEN_HEIGHT * 0.15 / 280)
crystal_3_sprite = load_image("assets/objects/crystals_3.png", SCREEN_HEIGHT * 0.15 / 280)
key_sprite = load_image("assets/objects/key.png", SCREEN_HEIGHT * 0.15 / 240)

# Враги кроме босса 12% по высоте экрана
bush_sprite = load_image("assets/enemies/enemy_bush.png", SCREEN_HEIGHT * 0.12 / 360)
worm_sprite = load_image("assets/enemies/enemy_worm.png", SCREEN_HEIGHT * 0.12 / 160)
flying_creature_sprite = load_image("assets/characters/flying_creature.png", SCREEN_HEIGHT * 0.12 / 200)
enemy_flying_creature_sprite = load_image("assets/enemies/enemy_flying_creature.png", SCREEN_HEIGHT * 0.12 / 200)
flipping_creature_sprite = load_image("assets/characters/flipping_creature.png", SCREEN_HEIGHT * 0.12 / 200)

# Дверь 40% по высоте экрана
door_sprite = load_image("assets/objects/door.png", SCREEN_HEIGHT * 0.40 / 460)

# Босс 40% по высоте экрана
boss_sprite = load_image("assets/enemies/enemy_boss.png", SCREEN_HEIGHT * 0.40 / 540)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Класс для персонажа Василия
class Vasily:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.speed = 4
        self.has_sword = False
        self.keys = 0
        self.crystals = 0
        self.animation_frame = 0
        self.attacking = False
        self.attack_timer = 0
        self.attack_duration = 15
        self.health = 100
        self.max_health = 100
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.current_scene = 0  # Для отслеживания текущей сцены
        self.last_transition_time = 0  # Время последнего перехода
        self.direction = "right"  # Направление персонажа: "left" или "right"
        
    def draw(self, screen):
        # Выбираем правильный спрайт в зависимости от состояния
        current_sprite = None
        if self.attacking and self.has_sword:
            current_sprite = hero_attack_sprite
        elif self.has_sword:
            current_sprite = hero_with_sword_sprite
        else:
            current_sprite = hero_no_sword_sprite
        
        # Получаем реальные размеры спрайта
        sprite_width = current_sprite.get_width() if current_sprite else self.width
        sprite_height = current_sprite.get_height() if current_sprite else self.height
        
        # Используем выбранный спрайт
        if current_sprite:
            # Отражаем спрайт если смотрит влево
            display_sprite = current_sprite
            if self.direction == "left":
                display_sprite = pygame.transform.flip(current_sprite, True, False)
            
            # Эффект неуязвимости
            if self.invulnerable and self.invulnerable_timer % 10 < 5:
                # Создаем полупрозрачную версию
                temp_sprite = display_sprite.copy()
                temp_sprite.set_alpha(128)
                screen.blit(temp_sprite, (self.x, self.y))
            else:
                screen.blit(display_sprite, (self.x, self.y))
        
        # Зона взаимодействия (кружочек) - ВИЗУАЛЬНЫЙ ДЕБАГ - с учетом направления
        if self.direction == "right":
            interaction_center_x = self.x + sprite_width + 40  # Справа от персонажа
        else:
            interaction_center_x = self.x - 40  # Слева от персонажа
        interaction_center_y = self.y + sprite_height // 2  # Посередине по вертикали
        pygame.draw.circle(screen, BLUE, (interaction_center_x, interaction_center_y), 80, 2)
        
        # Эффект атаки - хитбокс с учетом направления
        if self.attacking:
            if self.direction == "right":
                hitbox_x = self.x + sprite_width + 20  # Справа от персонажа
            else:
                hitbox_x = self.x - 20  # Слева от персонажа
            hitbox_y = self.y + sprite_height//2   # По центру по вертикали
            pygame.draw.circle(screen, YELLOW, (hitbox_x, hitbox_y), 15, 4)
            # Дополнительные частицы
            for i in range(5):
                particle_x = hitbox_x + random.randint(-10, 10)
                particle_y = hitbox_y + random.randint(-10, 10)
                pygame.draw.circle(screen, ORANGE, (particle_x, particle_y), 3)
        
        # Полоска здоровья
        self.draw_health_bar(screen)
    
    def draw_health_bar(self, screen):
        """Рисует полоску здоровья персонажа"""
        # Выбираем правильный спрайт
        current_sprite = None
        if self.attacking and self.has_sword:
            current_sprite = hero_attack_sprite
        elif self.has_sword:
            current_sprite = hero_with_sword_sprite
        else:
            current_sprite = hero_no_sword_sprite
        
        sprite_width = current_sprite.get_width() if current_sprite else self.width
        sprite_height = current_sprite.get_height() if current_sprite else self.height
        
        bar_width = 100
        bar_height = 8
        bar_x = self.x + sprite_width // 2 - bar_width // 2
        bar_y = self.y - 20
        
        # Фон полоски
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        # Текущее здоровье - С УЧЕТОМ РЕАЛЬНОГО HP
        current_width = max(0, int((self.health / self.max_health) * bar_width))
        if current_width > 0:
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, current_width, bar_height))
        # Рамка
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
    
    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_timer = 0
            return True
        return False
    
    def get_attack_hitbox(self):
        """Возвращает координаты хитбокса атаки"""
        if self.attacking:
            # Выбираем правильный спрайт
            current_sprite = None
            if self.attacking and self.has_sword:
                current_sprite = hero_attack_sprite
            elif self.has_sword:
                current_sprite = hero_with_sword_sprite
            else:
                current_sprite = hero_no_sword_sprite
            
            sprite_width = current_sprite.get_width() if current_sprite else self.width
            sprite_height = current_sprite.get_height() if current_sprite else self.height
            
            # Хитбокс в зависимости от направления
            if self.direction == "right":
                hitbox_x = self.x + sprite_width + 20  # Справа от персонажа
            else:
                hitbox_x = self.x - 20  # Слева от персонажа
            
            hitbox_y = self.y + sprite_height//2   # По центру по вертикали
            return (hitbox_x, hitbox_y, 15)  # x, y, radius
        return None
    
    def take_damage(self, damage):
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invulnerable_timer = 0
            if self.health <= 0:
                self.health = 0
                return True  # Персонаж умер
        return False
    
    def update(self):
        if self.attacking:
            self.attack_timer += 1
            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.attack_timer = 0
        
        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer >= 60:  # 1 секунда неуязвимости
                self.invulnerable = False
                self.invulnerable_timer = 0
    
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.animation_frame += 1

# Класс для объектов
class GameObject:
    def __init__(self, x, y, width, height, color, object_type, crystal_type=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.object_type = object_type
        self.collected = False
        self.hp = 100 if object_type == "boss" else 1
        self.max_hp = 100 if object_type == "boss" else 1
        self.animation_timer = 0
        self.original_y = y
        self.crystal_type = crystal_type  # Для фиксированного типа кристалла
        self.defeated = False  # Для босса
        self.attack_cooldown = 0  # Таймер перезарядки атаки босса
        self.attack_interval = 120  # Интервал между атаками босса (2 секунды при 60 FPS)
        
    def draw(self, screen):
        if not self.collected:
            # Анимация для ключей и кристаллов
            if self.object_type in ["key", "crystal"]:
                self.animation_timer += 1
                float_y = self.original_y + math.sin(self.animation_timer * 0.1) * 5
            
            # Используем только спрайты из assets
            if self.object_type == "sword_in_stone" and sword_sprite:
                screen.blit(sword_sprite, (self.x, self.y))
            elif self.object_type == "boss" and boss_sprite and not self.defeated:
                # Босс больше в 2 раза (только если не побежден)
                scaled_boss = pygame.transform.scale(boss_sprite, (self.width * 2, self.height * 2))
                screen.blit(scaled_boss, (self.x, self.y))
                self.draw_hp_bar(screen)
                
                # ВИЗУАЛЬНЫЙ ДЕБАГ - хитбокс босса
                boss_hitbox = self.get_hitbox()
                boss_x, boss_y, boss_w, boss_h = boss_hitbox
                pygame.draw.rect(screen, RED, (boss_x, boss_y, boss_w, boss_h), 3)
                
                # ВИЗУАЛЬНЫЙ ДЕБАГ - зона атаки босса
                attack_area = self.get_attack_area()
                if attack_area:
                    attack_x, attack_y, attack_w, attack_h = attack_area
                    pygame.draw.rect(screen, ORANGE, (attack_x, attack_y, attack_w, attack_h), 2)
            elif self.object_type == "key" and key_sprite:
                screen.blit(key_sprite, (self.x, float_y))
                # Свечение вокруг ключа
                pygame.draw.circle(screen, YELLOW, (self.x + 15, int(float_y) + 15), 25, 2)
            elif self.object_type == "door" and door_sprite:
                screen.blit(door_sprite, (self.x, self.y))
            elif self.object_type == "crystal" and crystal_1_sprite:
                # Используем фиксированный тип кристалла
                crystal_sprites = [crystal_1_sprite, crystal_2_sprite, crystal_3_sprite]
                crystal_sprite = crystal_sprites[self.crystal_type] if self.crystal_type is not None else crystal_1_sprite
                screen.blit(crystal_sprite, (self.x, float_y))
                # Эффект мерцания для кристаллов
                flicker_intensity = 0.5 + 0.5 * math.sin(self.animation_timer * 0.2)
                flicker_radius = int(20 * flicker_intensity)
                pygame.draw.circle(screen, PURPLE, (self.x + 15, int(float_y) + 15), flicker_radius, 2)
            elif self.object_type == "bush" and bush_sprite:
                screen.blit(bush_sprite, (self.x, self.y))
            elif self.object_type == "worm" and worm_sprite:
                screen.blit(worm_sprite, (self.x, self.y))
            elif self.object_type == "flying_creature" and flying_creature_sprite:
                screen.blit(flying_creature_sprite, (self.x, self.y))
            elif self.object_type == "enemy_flying_creature" and enemy_flying_creature_sprite:
                screen.blit(enemy_flying_creature_sprite, (self.x, self.y))
            elif self.object_type == "flipping_creature" and flipping_creature_sprite:
                screen.blit(flipping_creature_sprite, (self.x, self.y))
            
            # ВИЗУАЛЬНЫЙ ДЕБАГ - зона взаимодействия для объектов
            if self.object_type in ["sword_in_stone", "key", "crystal", "door"]:
                interaction_center_x = self.x + self.width // 2
                interaction_center_y = self.y + self.height // 2
                pygame.draw.circle(screen, CYAN, (interaction_center_x, interaction_center_y), 40, 2)
    
    def draw_hp_bar(self, screen):
        """Рисует полоску здоровья для босса"""
        if self.object_type == "boss" and not self.defeated:
            bar_width = 150
            bar_height = 12
            # Босс масштабирован в 2 раза
            boss_w = self.width * 2
            boss_h = self.height * 2
            bar_x = self.x + (boss_w - bar_width) // 2
            bar_y = self.y - 25
            
            # Фон полоски
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            # Текущее здоровье - С УЧЕТОМ РЕАЛЬНОГО HP
            current_width = max(0, int((self.hp / self.max_hp) * bar_width))
            if current_width > 0:
                pygame.draw.rect(screen, GREEN, (bar_x, bar_y, current_width, bar_height))
            # Рамка
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
            # Текст HP
            font = pygame.font.Font(None, 24)
            hp_text = font.render(f"BOSS HP: {self.hp}/{self.max_hp}", True, WHITE)
            screen.blit(hp_text, (bar_x, bar_y - 20))
    
    def take_damage(self, damage=1):
        """Наносит урон объекту"""
        if self.object_type == "boss":
            self.hp -= damage
            if self.hp <= 0:
                self.collected = True
                self.defeated = True
                return True
        return False
    
    def get_hitbox(self):
        """Возвращает хитбокс объекта для проверки столкновений"""
        if self.object_type == "boss":
            # Босс больше в 2 раза чем персонаж (по высоте в 2 раза больше)
            return (self.x, self.y, self.width * 2, self.height * 2)
        return (self.x, self.y, self.width, self.height)
    
    def update(self):
        """Обновляет состояние объекта (для босса - таймеры атаки)"""
        if self.object_type == "boss" and not self.defeated:
            self.attack_cooldown += 1
            if self.attack_cooldown >= self.attack_interval:
                self.attack_cooldown = 0  # Босс может атаковать
    
    def get_attack_area(self):
        """Возвращает зону атаки босса"""
        if self.object_type == "boss" and not self.defeated:
            # Зона атаки босса - область впереди него (только если не побежден)
            return (self.x - 100, self.y, 100, self.height * 2)
        return None

# Класс для сцены
class Scene:
    def __init__(self, name, background_color, objects):
        self.name = name
        self.background_color = background_color
        self.objects = objects
        self.completed = False
        self.animation_timer = 0
        
    def draw(self, screen):
        # Используем только фоновый слой с масштабированием под экран
        if background_far:
            # Масштабируем фон под размер экрана
            bg_scaled = pygame.transform.scale(background_far, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(bg_scaled, (0, 0))
        
        self.animation_timer += 1
        
        # Дополнительные элементы в зависимости от сцены
        if self.name == "sword_scene":
            # Добавляем кусты с анимацией
            if bush_sprite:
                for i in range(0, SCREEN_WIDTH, 200):
                    sway_offset = math.sin(self.animation_timer * 0.05 + i * 0.1) * 3
                    screen.blit(bush_sprite, (i, SCREEN_HEIGHT - 200 + sway_offset))
            
        elif self.name == "obstacle_scene":
            # Добавляем червей как препятствия
            if worm_sprite:
                for i in range(200, SCREEN_WIDTH, 300):
                    screen.blit(worm_sprite, (i, SCREEN_HEIGHT - 200))
                
        elif self.name == "boss_scene":
            # Темный эффект для боя с мерцанием (только если босс не побежден)
            boss_defeated = any(obj.object_type == "boss" and obj.defeated for obj in self.objects)
            if not boss_defeated:
                alpha = 50 + math.sin(self.animation_timer * 0.1) * 20
                screen.fill((int(alpha), int(alpha), int(alpha)), special_flags=pygame.BLEND_MULT)
            
        elif self.name == "keys_scene":
            # Пещера с летающими существами
            if flying_creature_sprite:
                for i in range(100, SCREEN_WIDTH, 250):
                    fly_offset = math.sin(self.animation_timer * 0.08 + i * 0.2) * 10
                    screen.blit(flying_creature_sprite, (i, SCREEN_HEIGHT - 300 + fly_offset))
            
            # Добавляем переворачивающихся существ
            if flipping_creature_sprite:
                for i in range(150, SCREEN_WIDTH, 400):
                    flip_offset = math.sin(self.animation_timer * 0.06 + i * 0.15) * 8
                    screen.blit(flipping_creature_sprite, (i, SCREEN_HEIGHT - 250 + flip_offset))
            
        elif self.name == "door_scene":
            # Новый остров с анимированным солнцем (без зеленой лужи)
            sun_y = 100 + math.sin(self.animation_timer * 0.05) * 5
            pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH - 100, int(sun_y)), 30)
        
        # Рисуем объекты
        for obj in self.objects:
            obj.draw(screen)

# Создание сцен
def create_scenes():
    scenes = []
    
    # Все объекты спавнятся в средней части экрана, не слишком низко и не слева
    # Объекты Y позиция: примерно на высоте 400-500 (средняя треть экрана)
    
    # Сцена 1: Доставание меча из камня + первый ключ
    sword_scene = Scene("sword_scene", (34, 139, 34), [
        GameObject(SCREEN_WIDTH//2 - 50, 400, 100, 100, GRAY, "sword_in_stone"),
        GameObject(300, 450, 30, 30, YELLOW, "key")
    ])
    scenes.append(sword_scene)
    
    # Сцена 2: Преодоление препятствий + второй ключ
    obstacle_scene = Scene("obstacle_scene", (135, 206, 235), [
        GameObject(600, 450, 30, 30, YELLOW, "key")
    ])
    scenes.append(obstacle_scene)
    
    # Сцена 3: Бой с боссом + третий ключ (НЕ МОЖЕТ БЫТЬ ПЕРВОЙ)
    boss_scene = Scene("boss_scene", (0, 50, 0), [
        GameObject(int(SCREEN_WIDTH * 2/3), SCREEN_HEIGHT - 300, 150, 200, GREEN, "boss"),  # На 2/3 ширины экрана
        GameObject(150, 450, 30, 30, YELLOW, "key")
    ])
    scenes.append(boss_scene)
    
    # Сцена 4: Поиск кристаллов (без ключей) - фиксированные типы
    keys_scene = Scene("keys_scene", (50, 25, 0), [
        GameObject(300, 450, 30, 30, PURPLE, "crystal", crystal_type=0),  # crystals_1
        GameObject(600, 400, 30, 30, PURPLE, "crystal", crystal_type=1),  # crystals_2
        GameObject(900, 420, 30, 30, PURPLE, "crystal", crystal_type=2)   # crystals_3
    ])
    scenes.append(keys_scene)
    
    # Сцена 5: Открытие двери
    door_scene = Scene("door_scene", (135, 206, 235), [
        GameObject(SCREEN_WIDTH - 150, 350, 100, 150, BROWN, "door")
    ])
    scenes.append(door_scene)
    
    return scenes

# Основная функция игры
def main():
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT
    
    clock = pygame.time.Clock()
    fullscreen = False  # Локальная переменная для полноэкранного режима
    # Правильная начальная позиция - нужно учесть высоту спрайта
    sprite_height = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
    initial_y = SCREEN_HEIGHT - sprite_height - 100  # На 100 пикселей выше низа экрана
    vasily = Vasily(50, initial_y)
    vasily.last_transition_time = pygame.time.get_ticks()  # Инициализируем время последнего перехода
    scenes = create_scenes()
    current_scene = 0
    scene_timer = 0
    scene_duration = 300  # 5 секунд на сцену при 60 FPS
    game_over = False
    victory = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Переключение полноэкранного режима
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        SCREEN_WIDTH = screen.get_width()
                        SCREEN_HEIGHT = screen.get_height()
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    pygame.display.set_caption("Приключения Василия - Финальная версия (F11 - полноэкранный режим)")
        
        if not game_over and not victory:
            # Управление Василием
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
                vasily.direction = "left"  # Поворачиваемся влево
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
                vasily.direction = "right"  # Поворачиваемся вправо
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            
            # Атака на SPACE (только если есть меч)
            if keys[pygame.K_SPACE]:
                vasily.attack()
            
            # Ограничение движения в пределах экрана (используем реальные размеры спрайта)
            # Получаем текущий спрайт
            temp_sprite = hero_no_sword_sprite
            if vasily.has_sword:
                temp_sprite = hero_with_sword_sprite
            if vasily.attacking and vasily.has_sword:
                temp_sprite = hero_attack_sprite
            
            sprite_width = temp_sprite.get_width() if temp_sprite else vasily.width
            sprite_height = temp_sprite.get_height() if temp_sprite else vasily.height
            
            # Разрешаем движение за правый край для триггера перехода (но не слишком далеко)
            # Движение происходит напрямую через move, но ограничиваем только левый край
            if vasily.x + dx * vasily.speed < 0:
                vasily.x = 0
            else:
                # Разрешаем выйти за правый край для триггера перехода (но не более чем на 50 пикселей)
                new_x = vasily.x + dx * vasily.speed
                if new_x > SCREEN_WIDTH + 50:
                    new_x = SCREEN_WIDTH + 50
                vasily.x = new_x
            
            # Позволяем спускаться ниже - можно спуститься на 100 пикселей ниже нижнего края спрайта
            max_y = SCREEN_HEIGHT - sprite_height + 100  # Можно спуститься чуть ниже
            if -100 <= vasily.y + dy * vasily.speed <= max_y:
                vasily.y += dy * vasily.speed
            
            # Обновление анимации
            vasily.animation_frame += 1
            
            # Обновляем Василия
            vasily.update()
            
            # Проверка взаимодействий с объектами
            current_scene_obj = scenes[current_scene]
            
            # Получаем реальные размеры спрайта персонажа
            current_sprite = None
            if vasily.attacking and vasily.has_sword:
                current_sprite = hero_attack_sprite
            elif vasily.has_sword:
                current_sprite = hero_with_sword_sprite
            else:
                current_sprite = hero_no_sword_sprite
            
            hero_sprite_width = current_sprite.get_width() if current_sprite else vasily.width
            hero_sprite_height = current_sprite.get_height() if current_sprite else vasily.height
            
            # Сначала проверяем босса отдельно - он должен всегда обновляться и атаковать
            for obj in current_scene_obj.objects:
                if obj.object_type == "boss":
                    # Обновляем босса
                    obj.update()
                    
                    # Проверяем атаку персонажа на босса
                    attack_hitbox = vasily.get_attack_hitbox()
                    if attack_hitbox and vasily.attacking:
                        hitbox_x, hitbox_y, hitbox_radius = attack_hitbox
                        boss_hitbox = obj.get_hitbox()
                        boss_x, boss_y, boss_w, boss_h = boss_hitbox
                        
                        # Проверяем столкновение хитбокса атаки с боссом
                        if (hitbox_x + hitbox_radius > boss_x and hitbox_x - hitbox_radius < boss_x + boss_w and
                            hitbox_y + hitbox_radius > boss_y and hitbox_y - hitbox_radius < boss_y + boss_h):
                            
                            if vasily.has_sword:
                                # Атака с мечом - урон 10 HP
                                if obj.take_damage(10):
                                    print("Босс побежден!")
                                    current_scene_obj.completed = True
                                else:
                                    print(f"Босс получил урон! HP: {obj.hp}/{obj.max_hp}")
                            else:
                                # Атака без меча - урон персонажу и переход на сцену меча
                                vasily.take_damage(20)
                                print("Василий атаковал босса без меча! Получил 20 урона!")
                                if vasily.health > 0:
                                    # Переход на сцену меча (первая сцена)
                                    current_scene = 0
                                    sprite_height_for_transition = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
                                    vasily.x = 50
                                    vasily.y = SCREEN_HEIGHT - sprite_height_for_transition - 100
                                    scene_timer = 0
                                    print(f"Переход на сцену меча: {scenes[current_scene].name}")
                                else:
                                    game_over = True
                    
                    # Проверяем атаку босса на персонажа (только если босс не побежден)
                    if not obj.defeated and obj.attack_cooldown == 0:  # Босс может атаковать
                        boss_attack_area = obj.get_attack_area()
                        if boss_attack_area:
                            attack_x, attack_y, attack_w, attack_h = boss_attack_area
                            
                            # Получаем реальные размеры спрайта персонажа
                            current_sprite_for_boss = hero_no_sword_sprite
                            if vasily.has_sword:
                                current_sprite_for_boss = hero_with_sword_sprite
                            if vasily.attacking and vasily.has_sword:
                                current_sprite_for_boss = hero_attack_sprite
                            
                            hero_sprite_width = current_sprite_for_boss.get_width() if current_sprite_for_boss else vasily.width
                            hero_sprite_height = current_sprite_for_boss.get_height() if current_sprite_for_boss else vasily.height
                            
                            # Проверяем, находится ли персонаж в зоне атаки босса (используем РЕАЛЬНЫЕ размеры)
                            if (vasily.x < attack_x + attack_w and vasily.x + hero_sprite_width > attack_x and
                                vasily.y < attack_y + attack_h and vasily.y + hero_sprite_height > attack_y):
                                # Босс атакует персонажа
                                if vasily.take_damage(15):  # 15 урона от атаки босса
                                    game_over = True
                                else:
                                    print("Босс атаковал Василия! -15 HP")
                                obj.attack_cooldown = -1  # Устанавливаем задержку перед следующей атакой
            
            # Теперь проверяем обычные объекты (ключи, кристаллы, меч, дверь)
            for obj in current_scene_obj.objects:
                if obj.object_type == "boss":
                    continue  # Босса уже обработали выше
                # Новая зона взаимодействия - с учетом направления (ИСПОЛЬЗУЕМ РЕАЛЬНЫЕ РАЗМЕРЫ СПРАЙТА)
                if vasily.direction == "right":
                    interaction_center_x = vasily.x + hero_sprite_width + 40  # Справа от персонажа
                else:
                    interaction_center_x = vasily.x - 40  # Слева от персонажа
                interaction_center_y = vasily.y + hero_sprite_height // 2
                # Центр объекта для проверки взаимодействия
                obj_center_x = obj.x + obj.width // 2
                obj_center_y = obj.y + obj.height // 2
                # Проверяем расстояние между центрами зон взаимодействия
                distance_x = abs(interaction_center_x - obj_center_x)
                distance_y = abs(interaction_center_y - obj_center_y)
                if (distance_x < 80 and distance_y < 80 and not obj.collected):
                    if obj.object_type == "sword_in_stone" and not vasily.has_sword and keys[pygame.K_e]:
                        vasily.has_sword = True
                        obj.collected = True
                        print("Василий достал меч из камня!")
                    elif obj.object_type == "key" and keys[pygame.K_e]:
                        vasily.keys += 1
                        obj.collected = True
                        print(f"Василий нашел ключ! Всего ключей: {vasily.keys}")
                    elif obj.object_type == "crystal" and keys[pygame.K_e]:
                        vasily.crystals += 1
                        obj.collected = True
                        print(f"Василий нашел кристалл! Всего кристаллов: {vasily.crystals}")
                    elif obj.object_type == "door" and vasily.keys >= 3 and keys[pygame.K_e]:
                        print("Василий открыл дверь и попал на новый остров!")
                        victory = True
                    elif obj.object_type == "boss":
                        # Обновляем босса
                        obj.update()
                        
                        # Проверяем атаку персонажа на босса
                        attack_hitbox = vasily.get_attack_hitbox()
                        if attack_hitbox and vasily.attacking:
                            hitbox_x, hitbox_y, hitbox_radius = attack_hitbox
                            boss_hitbox = obj.get_hitbox()
                            boss_x, boss_y, boss_w, boss_h = boss_hitbox
                            
                            # Проверяем столкновение хитбокса атаки с боссом
                            if (hitbox_x + hitbox_radius > boss_x and hitbox_x - hitbox_radius < boss_x + boss_w and
                                hitbox_y + hitbox_radius > boss_y and hitbox_y - hitbox_radius < boss_y + boss_h):
                                
                                if vasily.has_sword:
                                    # Атака с мечом - урон 10 HP
                                    if obj.take_damage(10):
                                        print("Босс побежден!")
                                        current_scene_obj.completed = True
                                    else:
                                        print(f"Босс получил урон! HP: {obj.hp}/{obj.max_hp}")
                                else:
                                    # Атака без меча - урон персонажу и переход на сцену меча
                                    vasily.take_damage(20)
                                    print("Василий атаковал босса без меча! Получил 20 урона!")
                                    if vasily.health > 0:
                                        # Переход на сцену меча (первая сцена)
                                        current_scene = 0
                                        sprite_height_for_transition = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
                                        vasily.x = 50
                                        vasily.y = SCREEN_HEIGHT - sprite_height_for_transition - 100
                                        scene_timer = 0
                                        print(f"Переход на сцену меча: {scenes[current_scene].name}")
                                    else:
                                        game_over = True
                        
                        # Проверяем атаку босса на персонажа (только если босс не побежден)
                        if not obj.defeated and obj.attack_cooldown == 0:  # Босс может атаковать
                            boss_attack_area = obj.get_attack_area()
                            if boss_attack_area:
                                attack_x, attack_y, attack_w, attack_h = boss_attack_area
                                
                                # Получаем реальные размеры спрайта персонажа
                                current_sprite_for_boss = hero_no_sword_sprite
                                if vasily.has_sword:
                                    current_sprite_for_boss = hero_with_sword_sprite
                                if vasily.attacking and vasily.has_sword:
                                    current_sprite_for_boss = hero_attack_sprite
                                
                                hero_sprite_width = current_sprite_for_boss.get_width() if current_sprite_for_boss else vasily.width
                                hero_sprite_height = current_sprite_for_boss.get_height() if current_sprite_for_boss else vasily.height
                                
                                # Проверяем, находится ли персонаж в зоне атаки босса (используем РЕАЛЬНЫЕ размеры)
                                if (vasily.x < attack_x + attack_w and vasily.x + hero_sprite_width > attack_x and
                                    vasily.y < attack_y + attack_h and vasily.y + hero_sprite_height > attack_y):
                                    # Босс атакует персонажа
                                    if vasily.take_damage(15):  # 15 урона от атаки босса
                                        game_over = True
                                    else:
                                        print("Босс атаковал Василия! -15 HP")
                                    obj.attack_cooldown = -1  # Устанавливаем задержку перед следующей атакой
            
            # Проверка смерти персонажа
            if vasily.health <= 0:
                game_over = True
            
            # Переход к следующей сцене по достижении краев экрана с ограничениями
            scene_timer += 1
            current_time = pygame.time.get_ticks()
            
            # Проверяем, прошла ли минимум 1 секунда с последнего перехода
            can_transition = current_time - vasily.last_transition_time >= 1000  # 1 секунда
            
            # Получаем реальный размер спрайта для проверки переходов
            temp_sprite_for_transition = hero_no_sword_sprite
            if vasily.has_sword:
                temp_sprite_for_transition = hero_with_sword_sprite
            if vasily.attacking and vasily.has_sword:
                temp_sprite_for_transition = hero_attack_sprite
            
            transition_sprite_width = temp_sprite_for_transition.get_width() if temp_sprite_for_transition else vasily.width
            
            # Проверяем переход к следующей сцене (правый край) - автоматический без клавиш
            at_right_edge = vasily.x >= SCREEN_WIDTH - 20
            can_advance = False
            if current_scene_obj.name == "sword_scene":
                # Из первой сцены вперед только если взяли меч
                can_advance = at_right_edge and can_transition and vasily.has_sword
            elif current_scene_obj.name == "boss_scene":
                # В сцене босса можно перейти только после победы
                can_advance = current_scene_obj.completed and can_transition and at_right_edge
            elif current_scene_obj.name == "door_scene":
                # Из сцены двери вперед переходим на сцену меча (круг)
                can_advance = at_right_edge and can_transition
            else:
                # obstacle_scene, keys_scene
                can_advance = at_right_edge and can_transition
            
            if can_advance:
                # Особая логика перехода из сцены двери: на сцену меча
                if current_scene_obj.name == "door_scene":
                    current_scene = 0
                else:
                    current_scene = (current_scene + 1) % len(scenes)
                scene_timer = 0
                sprite_height_for_transition = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
                # Появляется слева, но подальше от края чтобы не было бесконечного перехода
                vasily.x = 100
                vasily.y = SCREEN_HEIGHT - sprite_height_for_transition - 100  # Правильная позиция
                vasily.current_scene = current_scene
                vasily.last_transition_time = current_time
                print(f"Переход к сцене: {scenes[current_scene].name}")
            
            # Проверяем переход к предыдущей сцене (левый край) - автоматический без клавиш
            at_left_edge = vasily.x <= 10
            can_go_back = False
            if current_scene_obj.name == "sword_scene":
                # Из первой сцены назад можно только если есть 3 ключа
                can_go_back = at_left_edge and can_transition and vasily.keys >= 3
            elif current_scene_obj.name == "boss_scene":
                # Из босса назад можно только после победы
                can_go_back = current_scene_obj.completed and at_left_edge and can_transition
            else:
                # В остальных сценах - автоматический переход при достижении левого края
                can_go_back = at_left_edge and can_transition
            
            if can_go_back:
                current_scene = (current_scene - 1) % len(scenes)
                scene_timer = 0
                sprite_height_for_transition = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
                # Появляется справа, но подальше от края
                vasily.x = SCREEN_WIDTH - transition_sprite_width - 100
                vasily.y = SCREEN_HEIGHT - sprite_height_for_transition - 100  # Правильная позиция
                vasily.current_scene = current_scene
                vasily.last_transition_time = current_time
                print(f"Переход к предыдущей сцене: {scenes[current_scene].name}")
        
        # Отрисовка
        scenes[current_scene].draw(screen)
        vasily.draw(screen)
        
        # Интерфейс
        font = pygame.font.Font(None, 36)
        scene_text = font.render(f"Сцена: {scenes[current_scene].name}", True, BLACK)
        screen.blit(scene_text, (10, 10))
        
        if vasily.has_sword:
            sword_text = font.render("Меч: ✓", True, BLACK)
            screen.blit(sword_text, (10, 50))
        else:
            sword_text = font.render("Меч: ✗", True, RED)
            screen.blit(sword_text, (10, 50))
        
        keys_text = font.render(f"Ключи: {vasily.keys}/3", True, BLACK)
        screen.blit(keys_text, (10, 90))
        
        crystals_text = font.render(f"Кристаллы: {vasily.crystals}", True, BLACK)
        screen.blit(crystals_text, (10, 130))
        
        # Инструкции
        instruction_text = font.render("WASD - движение, SPACE - атака (только с мечом), E - взаимодействие", True, BLACK)
        screen.blit(instruction_text, (10, SCREEN_HEIGHT - 60))
        
        f11_hint_text = font.render("F11 - переключить полноэкранный режим", True, BLACK)
        screen.blit(f11_hint_text, (10, SCREEN_HEIGHT - 30))
        
        # Показываем сообщение если условие для перехода не выполнено
        current_scene_obj = scenes[current_scene]
        
        # Проверка условий для следующей сцены (правый край)
        at_right_edge = vasily.x >= SCREEN_WIDTH - 20
        at_left_edge = vasily.x <= 10
        
        if at_right_edge or at_left_edge:
            # Проверяем правый край
            if at_right_edge:
                # Подсказка для сцены меча: взять меч
                if current_scene_obj.name == "sword_scene" and not vasily.has_sword:
                    message_text = font.render("Возьмите меч (E) у камня", True, RED)
                    message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
                    screen.blit(message_text, message_rect)
                if current_scene_obj.name == "boss_scene":
                    if not current_scene_obj.completed:
                        # Босс не побежден
                        message_text = font.render("Победите босса мечом! (SPACE)", True, RED)
                        message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
                        screen.blit(message_text, message_rect)
                elif current_scene_obj.name == "door_scene":
                    if vasily.keys < 3:
                        # Недостаточно ключей
                        message_text = font.render(f"Соберите 3 ключа! У вас: {vasily.keys}/3", True, RED)
                        message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
                        screen.blit(message_text, message_rect)
                elif not can_transition:
                    # Задержка между переходами
                    message_text = font.render("Подождите 1 секунду...", True, YELLOW)
                    message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
                    screen.blit(message_text, message_rect)
            
            # Проверяем левый край
            elif at_left_edge:
                if current_scene_obj.name == "boss_scene":
                    if not current_scene_obj.completed:
                        message_text = font.render("← Вернуться нельзя! Победите босса!", True, ORANGE)
                        screen.blit(message_text, (10, SCREEN_HEIGHT - 60))
                elif current_scene_obj.name == "sword_scene":
                    if vasily.keys < 3:
                        message_text = font.render("← Вернуться нельзя! Нужно 3 ключа!", True, ORANGE)
                        screen.blit(message_text, (10, SCREEN_HEIGHT - 60))
                elif not can_transition:
                    # Задержка между переходами
                    message_text = font.render("← Подождите 1 секунду...", True, YELLOW)
                    screen.blit(message_text, (10, SCREEN_HEIGHT - 60))
        
        # Отладочная информация убрана
        
        # Экран победы
        if victory:
            victory_font = pygame.font.Font(None, 72)
            victory_text = victory_font.render("ПОБЕДА!", True, GREEN)
            victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(victory_text, victory_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Нажмите R для перезапуска", True, BLACK)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
            
            if keys[pygame.K_r]:
                # Перезапуск игры
                sprite_height = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
                initial_y = SCREEN_HEIGHT - sprite_height - 100
                vasily = Vasily(50, initial_y)
                scenes = create_scenes()
                current_scene = 0
                scene_timer = 0
                game_over = False
                victory = False
        
        # Экран поражения
        if game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("ПОРАЖЕНИЕ!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(game_over_text, game_over_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Нажмите R для перезапуска", True, BLACK)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
            
            if keys[pygame.K_r]:
                # Перезапуск игры
                sprite_height = hero_no_sword_sprite.get_height() if hero_no_sword_sprite else 60
                initial_y = SCREEN_HEIGHT - sprite_height - 100
                vasily = Vasily(50, initial_y)
                scenes = create_scenes()
                current_scene = 0
                scene_timer = 0
                game_over = False
                victory = False
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
