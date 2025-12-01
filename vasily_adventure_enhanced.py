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
pygame.display.set_caption("Приключения Василия - Улучшенная версия")

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
hero_sprite = load_image("assets/characters/hero_with_sword.png", SCREEN_HEIGHT * 0.20 / 460)

# Объекты 15% по высоте экрана
sword_sprite = load_image("assets/objects/sword_in_stone.png", SCREEN_HEIGHT * 0.15 / 180)
crystal_sprite = load_image("assets/objects/crystals_1.png", SCREEN_HEIGHT * 0.15 / 280)
key_sprite = load_image("assets/objects/key.png", SCREEN_HEIGHT * 0.15 / 240)

# Враги кроме босса 12% по высоте экрана
bush_sprite = load_image("assets/enemies/enemy_bush.png", SCREEN_HEIGHT * 0.12 / 360)
worm_sprite = load_image("assets/enemies/enemy_worm.png", SCREEN_HEIGHT * 0.12 / 160)
flying_creature_sprite = load_image("assets/characters/flying_creature.png", SCREEN_HEIGHT * 0.12 / 200)

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
        
    def draw(self, screen):
        # Используем только спрайт героя
        if hero_sprite:
            # Эффект неуязвимости
            if self.invulnerable and self.invulnerable_timer % 10 < 5:
                # Создаем полупрозрачную версию
                temp_sprite = hero_sprite.copy()
                temp_sprite.set_alpha(128)
                screen.blit(temp_sprite, (self.x, self.y))
            else:
                screen.blit(hero_sprite, (self.x, self.y))
        
        # Зона взаимодействия (кружочек)
        interaction_center_x = self.x + self.width // 2
        interaction_center_y = self.y + self.height // 2
        pygame.draw.circle(screen, BLUE, (interaction_center_x, interaction_center_y), 80, 2)
        
        # Эффект атаки
        if self.attacking:
            pygame.draw.circle(screen, YELLOW, (self.x + self.width + 30, self.y + self.height//2), 20, 4)
            # Дополнительные частицы
            for i in range(5):
                particle_x = self.x + self.width + 30 + random.randint(-15, 15)
                particle_y = self.y + self.height//2 + random.randint(-15, 15)
                pygame.draw.circle(screen, ORANGE, (particle_x, particle_y), 3)
        
        # Полоска здоровья
        self.draw_health_bar(screen)
    
    def draw_health_bar(self, screen):
        """Рисует полоску здоровья персонажа"""
        bar_width = 100
        bar_height = 8
        bar_x = self.x - 10
        bar_y = self.y - 15
        
        # Фон полоски
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        # Текущее здоровье
        current_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, current_width, bar_height))
        # Рамка
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
    
    def attack(self):
        if self.has_sword and not self.attacking:
            self.attacking = True
            self.attack_timer = 0
            return True
        return False
    
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
    def __init__(self, x, y, width, height, color, object_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.object_type = object_type
        self.collected = False
        self.hp = 3 if object_type == "boss" else 1
        self.max_hp = 3 if object_type == "boss" else 1
        self.animation_timer = 0
        self.original_y = y
        
    def draw(self, screen):
        if not self.collected:
            # Анимация для ключей и кристаллов
            if self.object_type in ["key", "crystal"]:
                self.animation_timer += 1
                float_y = self.original_y + math.sin(self.animation_timer * 0.1) * 5
            
            # Используем только спрайты из assets
            if self.object_type == "sword_in_stone" and sword_sprite:
                screen.blit(sword_sprite, (self.x, self.y))
            elif self.object_type == "boss" and boss_sprite:
                screen.blit(boss_sprite, (self.x, self.y))
                self.draw_hp_bar(screen)
            elif self.object_type == "key" and key_sprite:
                screen.blit(key_sprite, (self.x, float_y))
                # Свечение вокруг ключа
                pygame.draw.circle(screen, YELLOW, (self.x + 15, int(float_y) + 15), 25, 2)
            elif self.object_type == "door" and door_sprite:
                screen.blit(door_sprite, (self.x, self.y))
            elif self.object_type == "crystal" and crystal_sprite:
                screen.blit(crystal_sprite, (self.x, float_y))
                # Свечение вокруг кристалла
                pygame.draw.circle(screen, PURPLE, (self.x + 15, int(float_y) + 15), 20, 2)
            elif self.object_type == "bush" and bush_sprite:
                screen.blit(bush_sprite, (self.x, self.y))
            elif self.object_type == "worm" and worm_sprite:
                screen.blit(worm_sprite, (self.x, self.y))
            elif self.object_type == "flying_creature" and flying_creature_sprite:
                screen.blit(flying_creature_sprite, (self.x, self.y))
    
    def draw_hp_bar(self, screen):
        """Рисует полоску здоровья для босса"""
        if self.object_type == "boss":
            bar_width = 150
            bar_height = 12
            bar_x = self.x + (self.width - bar_width) // 2
            bar_y = self.y - 25
            
            # Фон полоски
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            # Текущее здоровье
            current_width = int((self.hp / self.max_hp) * bar_width)
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
                return True
        return False

# Класс для сцены
class Scene:
    def __init__(self, name, background_color, objects):
        self.name = name
        self.background_color = background_color
        self.objects = objects
        self.completed = False
        self.animation_timer = 0
        
    def draw(self, screen):
        # Используем только фоновый слой
        if background_far:
            screen.blit(background_far, (0, 0))
        
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
            # Темный эффект для боя с мерцанием
            alpha = 50 + math.sin(self.animation_timer * 0.1) * 20
            screen.fill((int(alpha), int(alpha), int(alpha)), special_flags=pygame.BLEND_MULT)
            
        elif self.name == "keys_scene":
            # Пещера с летающими существами
            if flying_creature_sprite:
                for i in range(100, SCREEN_WIDTH, 250):
                    fly_offset = math.sin(self.animation_timer * 0.08 + i * 0.2) * 10
                    screen.blit(flying_creature_sprite, (i, SCREEN_HEIGHT - 300 + fly_offset))
            
        elif self.name == "door_scene":
            # Новый остров с анимированным солнцем
            pygame.draw.ellipse(screen, GREEN, (0, SCREEN_HEIGHT - 200, SCREEN_WIDTH, 200))
            sun_y = 100 + math.sin(self.animation_timer * 0.05) * 5
            pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH - 100, int(sun_y)), 30)
        
        # Рисуем объекты
        for obj in self.objects:
            obj.draw(screen)

# Создание сцен
def create_scenes():
    scenes = []
    
    # Сцена 1: Доставание меча из камня + первый ключ
    sword_scene = Scene("sword_scene", (34, 139, 34), [
        GameObject(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT - 200, 100, 100, GRAY, "sword_in_stone"),
        GameObject(200, SCREEN_HEIGHT - 150, 30, 30, YELLOW, "key")
    ])
    scenes.append(sword_scene)
    
    # Сцена 2: Преодоление препятствий + второй ключ
    obstacle_scene = Scene("obstacle_scene", (135, 206, 235), [
        GameObject(600, SCREEN_HEIGHT - 200, 30, 30, YELLOW, "key")
    ])
    scenes.append(obstacle_scene)
    
    # Сцена 3: Бой с боссом + третий ключ
    boss_scene = Scene("boss_scene", (0, 50, 0), [
        GameObject(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 300, 150, 200, GREEN, "boss"),
        GameObject(100, SCREEN_HEIGHT - 150, 30, 30, YELLOW, "key")
    ])
    scenes.append(boss_scene)
    
    # Сцена 4: Поиск кристаллов (без ключей)
    keys_scene = Scene("keys_scene", (50, 25, 0), [
        GameObject(300, SCREEN_HEIGHT - 150, 30, 30, PURPLE, "crystal"),
        GameObject(600, SCREEN_HEIGHT - 200, 30, 30, PURPLE, "crystal"),
        GameObject(900, SCREEN_HEIGHT - 180, 30, 30, PURPLE, "crystal")
    ])
    scenes.append(keys_scene)
    
    # Сцена 5: Открытие двери
    door_scene = Scene("door_scene", (135, 206, 235), [
        GameObject(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 250, 100, 150, BROWN, "door")
    ])
    scenes.append(door_scene)
    
    return scenes

# Основная функция игры
def main():
    clock = pygame.time.Clock()
    vasily = Vasily(50, SCREEN_HEIGHT - 200)  # Появляется выше
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
        
        if not game_over and not victory:
            # Управление Василием
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            
            # Атака на SPACE
            if keys[pygame.K_SPACE]:
                vasily.attack()
            
            # Ограничение движения в пределах экрана
            if 0 <= vasily.x + dx * vasily.speed <= SCREEN_WIDTH - vasily.width:
                vasily.x += dx * vasily.speed
            if 0 <= vasily.y + dy * vasily.speed <= SCREEN_HEIGHT - vasily.height:
                vasily.y += dy * vasily.speed
            
            # Обновление анимации
            vasily.animation_frame += 1
            
            # Обновляем Василия
            vasily.update()
            
            # Проверка взаимодействий с объектами
            current_scene_obj = scenes[current_scene]
            for obj in current_scene_obj.objects:
                if (abs(vasily.x - obj.x) < 80 and abs(vasily.y - obj.y) < 80 and not obj.collected):
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
                    elif obj.object_type == "boss" and vasily.attacking:
                        # Атака босса
                        if obj.take_damage():
                            print("Босс побежден!")
                            current_scene_obj.completed = True
                        else:
                            print(f"Босс получил урон! HP: {obj.hp}/{obj.max_hp}")
            
            # Проверка смерти персонажа
            if vasily.health <= 0:
                game_over = True
            
            # Переход к следующей сцене
            scene_timer += 1
            if scene_timer >= scene_duration or current_scene_obj.completed:
                current_scene = (current_scene + 1) % len(scenes)
                scene_timer = 0
                vasily.x = 50
                vasily.y = SCREEN_HEIGHT - 200  # Появляется выше
                print(f"Переход к сцене: {scenes[current_scene].name}")
        
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
        
        keys_text = font.render(f"Ключи: {vasily.keys}/3", True, BLACK)
        screen.blit(keys_text, (10, 90))
        
        crystals_text = font.render(f"Кристаллы: {vasily.crystals}", True, BLACK)
        screen.blit(crystals_text, (10, 130))
        
        # Инструкции
        instruction_text = font.render("WASD - движение, SPACE - атака, E - взаимодействие", True, BLACK)
        screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
        
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
                vasily = Vasily(50, SCREEN_HEIGHT - 200)
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
                vasily = Vasily(50, SCREEN_HEIGHT - 200)
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
