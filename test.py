import pygame
import sys
import math
import random
from datetime import datetime
import pytz

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship Game")
pygame.display.set_icon(pygame.image.load('ship.png'))

# Colors
NAVY_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_BLUE = (100, 149, 237)
WAVE_BLUE = (65, 105, 225)
WOOD_BROWN = (139, 69, 19)
DARK_WOOD = (101, 67, 33)
SAND_COLOR = (238, 214, 175)
SKY_BLUE = (135, 206, 235)
SEA_BLUE = (0, 105, 148)
ISLAND_GREEN = (34, 139, 34)

# Font settings
title_font = pygame.font.Font(None, 74)
menu_font = pygame.font.Font(None, 50)
datetime_font = pygame.font.Font(None, 24)


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.hover_color = LIGHT_BLUE
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=12)

        text_surface = menu_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.wing_up = True
        self.wing_timer = 0
        self.speed = random.uniform(2, 4)

    def draw(self, surface):
        # Draw bird body
        pygame.draw.ellipse(surface, WHITE, (self.x, self.y, 20, 10))

        # Draw wings
        wing_height = -5 if self.wing_up else 5
        pygame.draw.line(surface, WHITE, (self.x + 10, self.y + 5),
                         (self.x + 15, self.y + wing_height), 2)
        pygame.draw.line(surface, WHITE, (self.x + 10, self.y + 5),
                         (self.x + 5, self.y + wing_height), 2)

    def update(self):
        self.x -= self.speed
        self.wing_timer += 1
        if self.wing_timer >= 10:
            self.wing_up = not self.wing_up
            self.wing_timer = 0

        if self.x < -30:
            self.x = SCREEN_WIDTH + 30
            self.y = random.randint(50, 200)

class Wave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time = random.random() * math.pi * 2

    def draw(self, surface):
        points = []
        for i in range(5):
            offset_x = i * 20
            offset_y = math.sin(self.time + i * 0.5) * 10
            points.append((self.x + offset_x, self.y + offset_y))

        if len(points) >= 2:
            pygame.draw.lines(surface, WAVE_BLUE, False, points, 3)

    def update(self):
        self.time += 0.05

class WreckedShip:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 15
        # Modified ship points for more detail
        self.ship_points = [
            (0, 0), (80, 0),  # Top deck
            (100, 20), (90, 40),  # Front
            (-20, 40), (-10, 20)  # Back
        ]
        self.mast_points = [
            (30, 0), (30, -50),  # Main mast
            (10, -40), (50, -40),  # Cross beam
            (30, -40), (30, -20)  # Lower mast
        ]
        # Add planks for detail
        self.plank_lines = [
            ((0, 10), (80, 10)),
            ((0, 20), (85, 20)),
            ((0, 30), (88, 30))
        ]

    def draw(self, surface):
        rotated_ship = []
        rotated_mast = []
        rotated_planks = []

        # Rotate ship points
        for point in self.ship_points:
            x = point[0] * math.cos(math.radians(self.angle)) - point[1] * math.sin(math.radians(self.angle))
            y = point[0] * math.sin(math.radians(self.angle)) + point[1] * math.cos(math.radians(self.angle))
            rotated_ship.append((x + self.x, y + self.y))

        # Rotate mast points
        for point in self.mast_points:
            x = point[0] * math.cos(math.radians(self.angle)) - point[1] * math.sin(math.radians(self.angle))
            y = point[0] * math.sin(math.radians(self.angle)) + point[1] * math.cos(math.radians(self.angle))
            rotated_mast.append((x + self.x, y + self.y))

        # Rotate plank lines
        for plank in self.plank_lines:
            rotated_plank = []
            for point in plank:
                x = point[0] * math.cos(math.radians(self.angle)) - point[1] * math.sin(math.radians(self.angle))
                y = point[0] * math.sin(math.radians(self.angle)) + point[1] * math.cos(math.radians(self.angle))
                rotated_plank.append((x + self.x, y + self.y))
            rotated_planks.append(rotated_plank)

        # Draw ship hull with wooden texture
        pygame.draw.polygon(surface, WOOD_BROWN, rotated_ship)
        pygame.draw.polygon(surface, DARK_WOOD, rotated_ship, 2)  # Outline

        # Draw planks
        for plank in rotated_planks:
            pygame.draw.line(surface, DARK_WOOD, plank[0], plank[1], 2)

        # Draw mast
        pygame.draw.lines(surface, WOOD_BROWN, False, rotated_mast[:2], 4)  # Main mast
        pygame.draw.lines(surface, WOOD_BROWN, False, rotated_mast[2:4], 3)  # Cross beam
        pygame.draw.lines(surface, DARK_WOOD, False, rotated_mast, 1)  # Outline

class GearIcon:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x - size / 2, y - size / 2, size, size)
        self.is_hovered = False

    def draw(self, surface):
        # Draw outer circle
        color = LIGHT_BLUE if self.is_hovered else WHITE
        pygame.draw.circle(surface, color, (self.x, self.y), self.size / 2, 2)

        # Draw inner circle
        pygame.draw.circle(surface, color, (self.x, self.y), self.size / 4, 2)

        # Draw teeth
        for i in range(8):
            angle = i * math.pi / 4
            start_x = self.x + (self.size / 2 - 5) * math.cos(angle)
            start_y = self.y + (self.size / 2 - 5) * math.sin(angle)
            end_x = self.x + (self.size / 2 + 5) * math.cos(angle)
            end_y = self.y + (self.size / 2 + 5) * math.sin(angle)
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Island:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = [
            (x, y),  # Top
            (x - 100, y + 80),  # Left
            (x - 70, y + 90),  # Left dent
            (x, y + 100),  # Middle bottom
            (x + 70, y + 90),  # Right dent
            (x + 100, y + 80),  # Right
        ]
        # Small details for the island
        self.palm_tree_positions = [
            (x - 50, y + 30),
            (x + 20, y + 20),
            (x - 20, y + 40)
        ]

    def draw(self, surface):
        # Draw main island shape
        pygame.draw.polygon(surface, SAND_COLOR, self.points)
        pygame.draw.polygon(surface, (200, 180, 150), self.points, 2)  # Island outline

        # Draw palm trees
        for palm_pos in self.palm_tree_positions:
            self.draw_palm_tree(surface, palm_pos[0], palm_pos[1])

    def draw_palm_tree(self, surface, x, y):
        # Draw trunk
        pygame.draw.line(surface, WOOD_BROWN, (x, y), (x - 10, y - 30), 4)
        # Draw leaves
        leaf_points = [
            (x - 25, y - 45), (x - 20, y - 35),
            (x - 5, y - 45), (x - 0, y - 35),
            (x + 15, y - 45), (x + 20, y - 35)
        ]
        for i in range(0, len(leaf_points), 2):
            pygame.draw.line(surface, ISLAND_GREEN, (x - 10, y - 30), leaf_points[i], 3)

class Ship:
    def __init__(self, name, size, color=(128, 128, 128)):
        self.name = name
        self.size = size
        self.color = color
        self.x = 0
        self.y = 0
        self.is_vertical = False
        self.is_placed = False
        self.cells = []  # Store the grid cells the ship occupies

    def draw(self, surface, grid_x, grid_y, cell_size):
        if not self.is_placed:
            # Draw the ship preview
            width = self.size * cell_size if not self.is_vertical else cell_size
            height = cell_size if not self.is_vertical else self.size * cell_size
            ship_rect = pygame.Rect(self.x, self.y, width, height)
            pygame.draw.rect(surface, self.color, ship_rect)
            pygame.draw.rect(surface, WHITE, ship_rect, 2)
        else:
            # Draw the placed ship
            for cell in self.cells:
                x = grid_x + cell[0] * cell_size
                y = grid_y + cell[1] * cell_size
                ship_rect = pygame.Rect(x, y, cell_size, cell_size)
                pygame.draw.rect(surface, self.color, ship_rect)
                pygame.draw.rect(surface, WHITE, ship_rect, 2)


class Grid:
    def __init__(self, x, y, cell_size=40):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.grid_size = 10
        self.cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.letters = 'ABCDEFGHIJ'

    def draw(self, surface):
        # Draw grid background
        grid_rect = pygame.Rect(self.x, self.y,
                                self.cell_size * self.grid_size,
                                self.cell_size * self.grid_size)
        pygame.draw.rect(surface, NAVY_BLUE, grid_rect)

        # Draw grid lines
        for i in range(self.grid_size + 1):
            # Vertical lines
            pygame.draw.line(surface, WHITE,
                             (self.x + i * self.cell_size, self.y),
                             (self.x + i * self.cell_size, self.y + self.grid_size * self.cell_size))
            # Horizontal lines
            pygame.draw.line(surface, WHITE,
                             (self.x, self.y + i * self.cell_size),
                             (self.x + self.grid_size * self.cell_size, self.y + i * self.cell_size))

        # Draw column numbers (1-10)
        for i in range(self.grid_size):
            num_text = datetime_font.render(str(i + 1), True, WHITE)
            num_rect = num_text.get_rect(center=(self.x + (i + 0.5) * self.cell_size,
                                                 self.y - 20))
            surface.blit(num_text, num_rect)

        # Draw row letters (A-J)
        for i in range(self.grid_size):
            letter_text = datetime_font.render(self.letters[i], True, WHITE)
            letter_rect = letter_text.get_rect(center=(self.x - 20,
                                                       self.y + (i + 0.5) * self.cell_size))
            surface.blit(letter_text, letter_rect)


def place_ships_screen():
    clock = pygame.time.Clock()
    grid = Grid(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)

    # Create ships with different colors
    ships = [
        Ship("Carrier", 5, (139, 69, 19)),  # Brown
        Ship("Battleship", 4, (169, 169, 169)),  # Dark Gray
        Ship("Destroyer", 4, (105, 105, 105)),  # Dim Gray
        Ship("Cruiser", 3, (128, 128, 128)),  # Gray
        Ship("Submarine", 2, (192, 192, 192))  # Light Gray
    ]

    current_ship = 0
    selected_ship = None

    # Initial position for the first ship
    ships[0].x = grid.x
    ships[0].y = grid.y + grid.cell_size * grid.grid_size + 50

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and selected_ship:
                    # Rotate ship
                    selected_ship.is_vertical = not selected_ship.is_vertical

            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_ship < len(ships):
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    ship = ships[current_ship]

                    # Check if click is within grid bounds
                    if (grid.x <= mouse_x <= grid.x + grid.cell_size * grid.grid_size and
                            grid.y <= mouse_y <= grid.y + grid.cell_size * grid.grid_size):

                        # Convert mouse position to grid coordinates
                        grid_x = (mouse_x - grid.x) // grid.cell_size
                        grid_y = (mouse_y - grid.y) // grid.cell_size

                        # Check if placement is valid
                        can_place = True
                        ship_cells = []

                        for i in range(ship.size):
                            if ship.is_vertical:
                                if grid_y + i >= grid.grid_size:
                                    can_place = False
                                    break
                                if grid.cells[grid_y + i][grid_x] is not None:
                                    can_place = False
                                    break
                                ship_cells.append((grid_x, grid_y + i))
                            else:
                                if grid_x + i >= grid.grid_size:
                                    can_place = False
                                    break
                                if grid.cells[grid_y][grid_x + i] is not None:
                                    can_place = False
                                    break
                                ship_cells.append((grid_x + i, grid_y))

                        if can_place:
                            # Place the ship
                            for cell in ship_cells:
                                grid.cells[cell[1]][cell[0]] = ship
                            ship.cells = ship_cells
                            ship.is_placed = True
                            current_ship += 1

                            if current_ship < len(ships):
                                ships[current_ship].x = grid.x
                                ships[current_ship].y = grid.y + grid.cell_size * grid.grid_size + 50

        # Update
        if current_ship < len(ships):
            selected_ship = ships[current_ship]
            if not selected_ship.is_placed:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                selected_ship.x = mouse_x - grid.cell_size // 2
                selected_ship.y = mouse_y - grid.cell_size // 2

        # Draw
        screen.fill(SKY_BLUE)

        # Draw instructions
        instructions = [
            "Place your ships on the grid",
            "Press 'R' to rotate",
            "Click to place ship",
            f"Currently placing: {ships[current_ship].name if current_ship < len(ships) else 'All ships placed'}"
        ]

        for i, text in enumerate(instructions):
            text_surface = datetime_font.render(text, True, WHITE)
            screen.blit(text_surface, (20, 20 + i * 30))

        # Draw grid
        grid.draw(screen)

        # Draw placed ships
        for ship in ships:
            if ship.is_placed:
                ship.draw(screen, grid.x, grid.y, grid.cell_size)

        # Draw current ship preview
        if current_ship < len(ships) and not ships[current_ship].is_placed:
            ships[current_ship].draw(screen, grid.x, grid.y, grid.cell_size)

        pygame.display.flip()
        clock.tick(60)


def main_menu():
    clock = pygame.time.Clock()

    # Create buttons
    buttons = [
        Button(SCREEN_WIDTH // 2 - 100, 200, 200, 50, "Start Game", NAVY_BLUE),
        Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Credits", NAVY_BLUE),
        Button(SCREEN_WIDTH // 2 - 100, 400, 200, 50, "Quit", NAVY_BLUE)
    ]

    # Create gear icon
    gear = GearIcon(SCREEN_WIDTH - 50, 50, 40)

    # Create birds
    birds = [Bird(SCREEN_WIDTH + i * 100, random.randint(50, 200)) for i in range(5)]

    # Create waves
    waves = [Wave(x * 100, SCREEN_HEIGHT - 100 + (x % 3) * 20) for x in range(10)]

    # Create island and ship (create once, not every frame)
    island = Island(SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 - 20)
    ship = WreckedShip(SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2 + 30)

    while True:
        # Get UTC time and convert to GMT+2
        utc_time = datetime.now(pytz.UTC)
        gmt2_timezone = pytz.timezone('Africa/Cairo')  # This gives GMT+2
        gmt2_time = utc_time.astimezone(gmt2_timezone)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle button events
            for button in buttons:
                if button.handle_event(event):
                    if button.text == "Start Game":
                        place_ships_screen()
                    elif button.text == "Credits":
                        print("Showing credits...")
                    elif button.text == "Quit":
                        pygame.quit()
                        sys.exit()
            # Handle gear icon events
            if gear.handle_event(event):
                print("Opening settings...")

        # Update birds and waves
        for bird in birds:
            bird.update()
        for wave in waves:
            wave.update()

        # Draw everything in the correct order
        # 1. Draw background (sky and sea)
        screen.fill(SKY_BLUE)  # Fill the entire screen with sky color
        pygame.draw.rect(surface=screen, color=SEA_BLUE,
                         rect=(0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # 2. Draw background elements
        island.draw(screen)  # Draw island first
        for wave in waves:  # Draw waves
            wave.draw(screen)
        ship.draw(screen)  # Draw ship on top of waves

        # 3. Draw birds
        for bird in birds:
            bird.draw(screen)

        # 4. Draw UI elements
        # Draw title with shadow effect
        title_shadow = title_font.render("BATTLESHIP", True, (0, 0, 64))
        title_text = title_font.render("BATTLESHIP", True, WHITE)
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 102))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_text, title_rect)

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        # Draw gear icon
        gear.draw(screen)

        # Draw GMT+2 time
        gmt2_text = f"Local Time (GMT+2): {gmt2_time.strftime('%Y-%m-%d %H:%M:%S')}"
        gmt2_surface = datetime_font.render(gmt2_text, True, WHITE)
        gmt2_rect = gmt2_surface.get_rect(topleft=(10, 10))

        # Draw background for time
        pygame.draw.rect(screen, NAVY_BLUE, (5, 5, gmt2_rect.width + 10, 25))
        pygame.draw.rect(screen, WHITE, (5, 5, gmt2_rect.width + 10, 25), 1)

        # Draw time
        screen.blit(gmt2_surface, gmt2_rect)

        # Draw user login with background
        login_text = f"Current User's Login: youssefghgg"
        login_surface = datetime_font.render(login_text, True, WHITE)
        login_rect = login_surface.get_rect(topleft=(10, 35))
        pygame.draw.rect(screen, NAVY_BLUE, (5, 30, login_rect.width + 10, login_rect.height + 10))
        pygame.draw.rect(screen, WHITE, (5, 30, login_rect.width + 10, login_rect.height + 10), 1)
        screen.blit(login_surface, login_rect)

        # Add version number
        version_text = "v1.0.0"
        version_surface = datetime_font.render(version_text, True, GRAY)
        version_rect = version_surface.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        screen.blit(version_surface, version_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()