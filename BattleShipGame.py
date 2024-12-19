import pygame
from PIL.ImageOps import scale
import random

# Initialize pygame
pygame.init()

# Create the screen
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
rows = 10
cols = 10
cells_size = 50


# Title and Icon
pygame.display.set_caption("Battleships")
icon = pygame.image.load('ship.png')  # Ensure this file exists
pygame.display.set_icon(icon)
background_image = pygame.image.load('background.jpeg')
scaled_image = pygame.transform.scale(background_image,(width,height))
title_font = pygame.font.SysFont('Comic Sans MS', 70)
title_text = title_font.render("BattleShips", True, (255, 255, 255))
title_rect = title_text.get_rect(center=(width // 2, 100))

# Game Functions
def CreatedGameGrid(rows, cols, cells_size, position):
    start_x = position[0]
    start_y = position[1]
    grid = []
    for row in range(rows):
        row_x = []
        for col in range(cols):
            row_x.append((start_x, start_y))
            start_x += cells_size
        grid.append(row_x)
        start_x = position[0]
        start_y += cells_size
    return grid

def UPGameLogic(rows, cols):
    # Updates game grid space and x with ships
    logic = []
    for row in range(rows):
        row_x = []
        for col in range(cols):
            row_x.append(" ")
            logic.append(row_x)
        return logic

def printLogic():
    print("Player Grid".center(50, '#'))
    for x in pGameLogic:
        print(x)
    print('Computer Grid'.center(50, '#'))
    for x in cGameLogic:
        print(x)
def game_mode_menu():
    menu_running = True
    while menu_running:
        # Draw the background first
        screen.blit(scaled_image, (0, 0))
        screen.blit(title_text, title_rect)

        # Define button rectangles
        singleplayer_button = pygame.Rect(width // 2 - 150, 200, 300, 50)
        multiplayer_button = pygame.Rect(width // 2 - 150, 300, 300, 50)
        back_button = pygame.Rect(width // 2 - 150, 400, 300, 50)

        # Draw buttons
        draw_button("Singleplayer", (0, 255, 0), singleplayer_button)
        draw_button("Multiplayer", (0, 255, 255), multiplayer_button)
        draw_button("Back", (255, 0, 0), back_button)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if singleplayer_button.collidepoint(event.pos):
                    return 'singleplayer'
                elif multiplayer_button.collidepoint(event.pos):
                    return 'multiplayer'
                elif back_button.collidepoint(event.pos):
                    return 'back'

        pygame.display.update()

def draw_grid_with_labels(x_start, y_start, cell_size, rows, cols):
    # Draw the grid
    for row in range(rows):
        for col in range(cols):
            x = x_start + col * cell_size
            y = y_start + row * cell_size
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(x, y, cell_size, cell_size), 1)

    # Draw row labels (A-J)
    font = pygame.font.SysFont('Arial', 30)
    for i in range(rows):
        label = font.render(chr(65 + i), True, (255, 255, 255))  # A=65 in ASCII
        screen.blit(label, (x_start - 30, y_start + i * cell_size + 10))

    # Draw column labels (1-10)
    for j in range(cols):
        label = font.render(str(j + 1), True, (255, 255, 255))
        screen.blit(label, (x_start + j * cell_size + 15, y_start - 30))

def snap_to_grid(x, y, grid_start_x, grid_start_y, cell_size):
    grid_x = ((x - grid_start_x) // cell_size) * cell_size + grid_start_x
    grid_y = ((y - grid_start_y) // cell_size) * cell_size + grid_start_y
    return grid_x, grid_y

def singleplayer_setup():
    running = True

    ships = [
        {"name": "Submarine", "rect": pygame.Rect(600, 100, cells_size * 2, cells_size), "horizontal": True, "dragging": False},
        {"name": "Cruiser", "rect": pygame.Rect(600, 200, cells_size * 3, cells_size), "horizontal": True, "dragging": False},
        {"name": "Battleship", "rect": pygame.Rect(600, 300, cells_size * 4, cells_size), "horizontal": True, "dragging": False},
        {"name": "Destroyer", "rect": pygame.Rect(600, 400, cells_size * 4, cells_size), "horizontal": True, "dragging": False},
        {"name": "Air Carrier", "rect": pygame.Rect(600, 500, cells_size * 5, cells_size), "horizontal": True, "dragging": False}
    ]
    selected_ship = None
    all_ships_placed = False
    start_button = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return 'quit'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if all_ships_placed and start_button and start_button.collidepoint(event.pos):
                    return ships  # Return the player's ship positions
                for ship in ships:
                    if ship["rect"].collidepoint(event.pos):
                        ship["dragging"] = True
                        selected_ship = ship
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_ship:
                    selected_ship["dragging"] = False
                    selected_ship["rect"].x, selected_ship["rect"].y = snap_to_grid(
                        selected_ship["rect"].x,
                        selected_ship["rect"].y,
                        50, 100, cells_size
                    )
                    selected_ship = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and selected_ship:
                    rotate_ship(selected_ship)

        if selected_ship and selected_ship["dragging"]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_ship["rect"].center = (mouse_x, mouse_y)

        all_ships_placed = all(
            50 <= ship["rect"].x < 50 + cols * cells_size and
            100 <= ship["rect"].y < 100 + rows * cells_size
            for ship in ships
        )

        screen.blit(scaled_image, (0, 0))

        setup_font = pygame.font.SysFont('Arial', 50)
        setup_text = setup_font.render("Player 1: Pick Positions", True, (255, 255, 255))
        setup_rect = setup_text.get_rect(center=(width // 2, 50))
        screen.blit(setup_text, setup_rect)

        draw_grid_with_labels(50, 100, cells_size, rows, cols)

        for ship in ships:
            pygame.draw.rect(screen, (0, 255, 0), ship["rect"])
            font = pygame.font.SysFont('Arial', 20)
            label = font.render(ship["name"], True, (255, 255, 255))
            screen.blit(label, (ship["rect"].x, ship["rect"].y - 20))

        if all_ships_placed:
            start_button = pygame.Rect(width - 200, height - 100, 150, 50)
            draw_button("Start", (0, 255, 0), start_button)

        pygame.display.update()



def start_game(player_ships):
    running = True

    # Generate computer ships randomly
    computer_ships = generate_computer_ships()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return 'quit'

        screen.blit(scaled_image, (0, 0))

        # Draw grids
        draw_grid_with_labels(50, 100, cells_size, rows, cols)  # Player grid
        draw_grid_with_labels(450, 100, cells_size, rows, cols)  # Computer grid

        # Draw player ships
        for ship in player_ships:
            pygame.draw.rect(screen, (0, 255, 0), ship["rect"])

        # Draw computer ships for now (hidden in actual gameplay)
        for ship in computer_ships:
            pygame.draw.rect(screen, (255, 0, 0), ship["rect"])

        pygame.display.update()


def generate_computer_ships():
    ships = [
        {"name": "Submarine", "size": 2},
        {"name": "Cruiser", "size": 3},
        {"name": "Battleship", "size": 4},
        {"name": "Destroyer", "size": 4},
        {"name": "Air Carrier", "size": 5},
    ]
    placed_ships = []

    for ship in ships:
        placed = False
        while not placed:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                start_x = random.randint(50, 50 + (cols - ship["size"]) * cells_size)
                start_y = random.randint(100, 100 + (rows - 1) * cells_size)
                rect = pygame.Rect(start_x, start_y, ship["size"] * cells_size, cells_size)
            else:
                start_x = random.randint(50, 50 + (cols - 1) * cells_size)
                start_y = random.randint(100, 100 + (rows - ship["size"]) * cells_size)
                rect = pygame.Rect(start_x, start_y, cells_size, ship["size"] * cells_size)

            # Ensure no overlap
            if not any(r["rect"].colliderect(rect) for r in placed_ships):
                placed_ships.append({"name": ship["name"], "rect": rect})
                placed = True

    return placed_ships


def rotate_ship(ship):
    """Rotate the ship between horizontal and vertical."""
    if ship["horizontal"]:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    else:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    ship["horizontal"] = not ship["horizontal"]


def snap_to_grid(x, y, grid_start_x, grid_start_y, cell_size):
    """Snap the ship to the nearest grid cell."""
    snapped_x = round((x - grid_start_x) / cell_size) * cell_size + grid_start_x
    snapped_y = round((y - grid_start_y) / cell_size) * cell_size + grid_start_y
    return snapped_x, snapped_y


# Loading Game
pGameGrid = CreatedGameGrid(rows, cols, cells_size, (50, 50))
pGameLogic = UPGameLogic(rows, cols)

cGameGrid = CreatedGameGrid(rows, cols, cells_size, (width - (rows * cells_size), 50))
cGameLogic = UPGameLogic(rows, cols)

# Menu Functions
def draw_button(text, color, rect):
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.SysFont("Arial", 40)
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (rect.x + 10, rect.y + 10))

def main_menu():
    menu_running = True
    while menu_running:
        # Draw the background first
        screen.blit(scaled_image, (0, 0))
        screen.blit(title_text, title_rect)

        # Define button rectangles
        start_button = pygame.Rect(width // 2 - 100, 200, 200, 50)
        settings_button = pygame.Rect(width // 2 - 100, 300, 200, 50)
        quit_button = pygame.Rect(width // 2 - 100, 400, 200, 50)

        # Draw buttons
        draw_button("Start Game", (0, 255, 0), start_button)
        draw_button("Settings", (255, 255, 0), settings_button)
        draw_button("Quit", (255, 0, 0), quit_button)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return 'start'
                elif settings_button.collidepoint(event.pos):
                    return 'settings'
                elif quit_button.collidepoint(event.pos):
                    return 'quit'

        pygame.display.update()


# Game Loop (after the menu)
def game_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the background first
        screen.blit(scaled_image, (0, 0))


        # Draw the game grid
        for row in pGameGrid:
            for cell in row:
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(cell[0], cell[1], cells_size, cells_size), 1)

        for row in cGameGrid:
            for cell in row:
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(cell[0], cell[1], cells_size, cells_size), 1)

        pygame.display.update()

# Main flow
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    menu_result = main_menu()

    if menu_result == 'start':
        mode_result = game_mode_menu()  # Open game mode menu
        if mode_result == 'singleplayer':
            print("Singleplayer mode selected")
            player_ships = singleplayer_setup()  # Call singleplayer setup
            if player_ships != 'quit':  # If the user doesn't quit, start the game
                start_game(player_ships)
        elif mode_result == 'multiplayer':
            print("Multiplayer mode selected")
            game_loop()  # Extend this to handle multiplayer
        elif mode_result == 'back':
            continue  # Return to the main menu
        elif mode_result == 'quit':
            running = False


    elif menu_result == 'settings':
        print("Settings clicked")
    elif menu_result == 'quit':
        running = False
    # Draw player's grid (left) with ships
    draw_grid_with_labels(50, 100, cells_size, rows, cols)

    # Draw opponent's grid (right)
    draw_grid_with_labels(width - cols * cells_size - 50, 100, cells_size, rows, cols)
    # R-G-B
    screen.blit(scaled_image, (0, 0))
    screen.blit(title_text, title_rect)
    pygame.display.update()


pygame.quit()
