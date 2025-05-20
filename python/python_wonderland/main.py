import pygame
import sys
import math
import time
from tween import Tween

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
DEG2RAD = math.pi / 180

# Colors
GRASS_COLOR = (124, 187, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (245, 215, 178)
RED = (224, 94, 94)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (48, 48, 48)
LIGHT_BLUE = (163, 204, 241)
GREEN = (58, 95, 56)

# Create the game window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Alice in Wonderland - Python Version")
clock = pygame.time.Clock()

# Game state
class GameState:
    def __init__(self):
        self.door_open = False
        self.door_time = -9999
        self.start_time = time.time()
    
    def get_server_time(self):
        return time.time() - self.start_time
    
    def toggle_door(self):
        self.door_open = not self.door_open
        self.door_time = self.get_server_time()
    
    def emit_signal(self, signal_name, data):
        print(f"Signal emitted: {signal_name} with data: {data}")

state = GameState()

# Animations
open_door_tween = Tween({"rotation": 0}).to({"rotation": 120}, 1.5, Tween.quad_in_out)
close_door_tween = Tween({"rotation": 120}).to({"rotation": 0}, 1.5, Tween.quad_in_out)
swirl_tween = Tween({"rotation": 0}).to({"rotation": 360}, 5, Tween.linear)
swirl_tween.loop()

# Interactive elements
class RabbitHole:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.outer_radius = radius
        self.inner_radius = radius * 0.6
        self.rotation = 0
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.font = pygame.font.SysFont(None, 24)
    
    def update(self, current_time):
        swirl_tween.set(current_time * 0.5)
        self.rotation = swirl_tween.value["rotation"]
    
    def draw(self, surface):
        # Draw outer circle
        pygame.draw.circle(surface, BROWN, (self.x, self.y), self.outer_radius)
        
        # Draw inner spinning circle (simplified)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), self.inner_radius)
        
        # Add swirl effect (simplified)
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            end_x = self.x + math.cos(angle) * self.inner_radius * 0.8
            end_y = self.y + math.sin(angle) * self.inner_radius * 0.8
            pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)
        
        # Draw text
        text = self.font.render("Rabbit Hole", True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y - self.outer_radius - 15))
        surface.blit(text, text_rect)
    
    def is_clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        
        # Check if click is within the inner circle
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance <= self.inner_radius
    
    def handle_click(self):
        print("Teleporting through the rabbit hole!")
        state.emit_signal("RabbitHoleEntered", {"playerId": "player1"})

class LookingGlassDoor:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.frame_width = width * 0.3
        self.door_width = width * 0.7
        self.rotation = 0
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self, current_time):
        tween = open_door_tween if state.door_open else close_door_tween
        tween.set(current_time - state.door_time)
        self.rotation = tween.value["rotation"]
    
    def draw(self, surface):
        # Draw door frame
        frame_rect = pygame.Rect(self.x, self.y, self.frame_width, self.height)
        pygame.draw.rect(surface, BROWN, frame_rect)
        
        # Calculate door position based on rotation
        max_swing = self.door_width * 0.8  # Maximum distance the door can swing open
        swing_amount = max_swing * math.sin(math.radians(self.rotation))
        
        # Draw door
        door_rect = pygame.Rect(
            self.x + self.frame_width - swing_amount, 
            self.y,
            self.door_width,
            self.height
        )
        pygame.draw.rect(surface, LIGHT_BLUE, door_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def handle_click(self):
        state.toggle_door()

# Create interactive elements
rabbit_hole = RabbitHole(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100, 50)
looking_glass = LookingGlassDoor(50, WINDOW_HEIGHT // 2 - 75, 60, 150)

# Main game loop
running = True
while running:
    current_time = state.get_server_time()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if rabbit_hole.is_clicked(event.pos):
                    rabbit_hole.handle_click()
                elif looking_glass.is_clicked(event.pos):
                    looking_glass.handle_click()
    
    # Update
    rabbit_hole.update(current_time)
    looking_glass.update(current_time)
    
    # Draw
    window.fill(GRASS_COLOR)
    
    # Draw checkerboard pattern
    board_size = 8
    tile_size = 40
    start_x = (WINDOW_WIDTH - board_size * tile_size) // 2
    start_y = (WINDOW_HEIGHT - board_size * tile_size) // 2
    
    for row in range(board_size):
        for col in range(board_size):
            is_light = (row + col) % 2 == 0
            color = LIGHT_GRAY if is_light else DARK_GRAY
            rect = pygame.Rect(
                start_x + col * tile_size,
                start_y + row * tile_size,
                tile_size,
                tile_size
            )
            pygame.draw.rect(window, color, rect)
    
    # Draw giant mushrooms (simplified)
    def draw_mushroom(x, y, stem_height, cap_radius, stem_radius):
        pygame.draw.rect(window, LIGHT_BROWN, 
                        (x - stem_radius, y - stem_height, stem_radius * 2, stem_height))
        pygame.draw.circle(window, RED, (x, y - stem_height), cap_radius)
    
    draw_mushroom(100, 400, 40, 30, 10)
    draw_mushroom(300, 500, 30, 25, 8)
    draw_mushroom(700, 350, 50, 40, 12)
    
    # Draw Cheshire cat tree (simplified)
    tree_x, tree_y = WINDOW_WIDTH - 150, 200
    pygame.draw.rect(window, BROWN, (tree_x - 15, tree_y, 30, 100))
    pygame.draw.circle(window, GREEN, (tree_x, tree_y), 50)
    
    # Draw smile on tree
    pygame.draw.arc(window, WHITE, (tree_x - 25, tree_y - 10, 50, 30), 0, math.pi, 3)
    
    # Draw tea party table (simplified)
    table_x, table_y = 150, 150
    pygame.draw.circle(window, BROWN, (table_x, table_y), 40)
    pygame.draw.rect(window, WHITE, (table_x - 20, table_y - 10, 15, 15))
    pygame.draw.circle(window, WHITE, (table_x + 10, table_y + 5), 8)
    
    # Draw interactive elements
    rabbit_hole.draw(window)
    looking_glass.draw(window)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
