import pygame
from PIL.ImageOps import scale
import random
import time

# Initialize pygame
pygame.init()

# Create the screen
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
rows = 10
cols = 10
cells_size = 33
current_turn = "player"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Title and Icon
pygame.display.set_caption("Battleships")
icon = pygame.image.load('ship.png')  # Ensure this file exists
pygame.display.set_icon(icon)
background_image = pygame.image.load('background.jpeg')
scaled_image = pygame.transform.scale(background_image,(width,height))
title_font = pygame.font.SysFont('Comic Sans MS', 70)
title_text = title_font.render("BattleShips", True, WHITE)
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
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, cell_size, cell_size), 1)

    # Draw row labels (A-J)
    font = pygame.font.SysFont('Arial', 30)
    for i in range(rows):
        label = font.render(chr(65 + i), True, WHITE)  # A=65 in ASCII
        screen.blit(label, (x_start - 30, y_start + i * cell_size + 10))

    # Draw column labels (1-10)
    for j in range(cols):
        label = font.render(str(j + 1), True, WHITE)
        screen.blit(label, (x_start + j * cell_size + 15, y_start - 30))
def snap_to_grid(x, y, grid_start_x, grid_start_y, cell_size, grid_width, grid_height, ship_width, ship_height):
    """Snap the ship to the nearest valid grid cell, respecting grid boundaries."""
    snapped_x = round((x - grid_start_x) / cell_size) * cell_size + grid_start_x
    snapped_y = round((y - grid_start_y) / cell_size) * cell_size + grid_start_y

    # Ensure the ship stays within the grid boundaries
    if snapped_x + ship_width > grid_start_x + grid_width:
        snapped_x = grid_start_x + grid_width - ship_width
    if snapped_y + ship_height > grid_start_y + grid_height:
        snapped_y = grid_start_y + grid_height - ship_height
    if snapped_x < grid_start_x:
        snapped_x = grid_start_x
    if snapped_y < grid_start_y:
        snapped_y = grid_start_y

    return snapped_x, snapped_y
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
                    # Snap to grid with boundary checks
                    snapped_x, snapped_y = snap_to_grid(
                        selected_ship["rect"].x,
                        selected_ship["rect"].y,
                        50,  # Grid start x
                        100,  # Grid start y
                        cells_size,  # Cell size
                        cols * cells_size,  # Grid width
                        rows * cells_size,  # Grid height
                        selected_ship["rect"].width,  # Ship width
                        selected_ship["rect"].height,  # Ship height
                    )
                    # Set snapped position
                    selected_ship["rect"].x, selected_ship["rect"].y = snapped_x, snapped_y
                    # Check for overlap and resolve it
                    if any(ship != selected_ship and selected_ship["rect"].colliderect(ship["rect"]) for ship in ships):
                        nearest_x, nearest_y = find_nearest_valid_position(selected_ship, ships)
                        selected_ship["rect"].x, selected_ship["rect"].y = nearest_x, nearest_y

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
        setup_text = setup_font.render("Player 1: Pick Positions", True, WHITE)
        setup_rect = setup_text.get_rect(center=(width // 2, 50))
        screen.blit(setup_text, setup_rect)
        draw_grid_with_labels(50, 100, cells_size, rows, cols)
        for ship in ships:
            pygame.draw.rect(screen, GREEN, ship["rect"])
            font = pygame.font.SysFont('Arial', 20)
            label = font.render(ship["name"], True, WHITE)
            screen.blit(label, (ship["rect"].x, ship["rect"].y - 20))
        if all_ships_placed:
            start_button = pygame.Rect(width - 200, height - 100, 150, 50)
            draw_button("Start", GREEN, start_button)
        pygame.display.update()
def computer_turn():
    # Pick random row and column
    row = random.randint(0, rows - 1)
    col = random.randint(0, cols - 1)

    # Player grid position
    grid_start_x = 50
    grid_start_y = 100

    # Highlight the chosen cell
    pygame.draw.rect(screen, RED,
                     pygame.Rect(grid_start_x + col * cells_size,
                                 grid_start_y + row * cells_size,
                                 cells_size, cells_size))
def find_nearest_valid_position(selected_ship, ships):
    valid_positions = []

    for row in range(rows):
        for col in range(cols):
            grid_x = 50 + col * cells_size
            grid_y = 100 + row * cells_size

            # Ensure the ship fits within the grid boundaries
            if grid_x + selected_ship["rect"].width <= 50 + cols * cells_size and \
               grid_y + selected_ship["rect"].height <= 100 + rows * cells_size:

                # Create a temp rect for collision checking
                temp_rect = pygame.Rect(grid_x, grid_y, selected_ship["rect"].width, selected_ship["rect"].height)

                # Ensure no overlap with other ships
                if not any(temp_rect.colliderect(ship["rect"]) for ship in ships if ship != selected_ship):
                    valid_positions.append((grid_x, grid_y))

    # Find the closest valid position
    current_center = selected_ship["rect"].center
    nearest_position = min(valid_positions, key=lambda pos: (pos[0] - current_center[0])**2 + (pos[1] - current_center[1])**2)
    return nearest_position
def check_collision(new_ship_rect, all_ships):
    """Check if the new ship overlaps with any existing ships."""
    for ship in all_ships:
        if ship["rect"].colliderect(new_ship_rect):
            return True  # Collision detected
    return False  # No collision
def start_game(player_ships):
    running = True

    # Generate computer ships randomly
    computer_ships = generate_computer_ships()

    # Create grids to track shot status
    computer_grid_status = [[None for _ in range(cols)] for _ in range(rows)]  # Computer grid: None = untouched, 'hit', or 'miss'
    player_grid_status = [[None for _ in range(cols)] for _ in range(rows)]  # Player grid: None = untouched, 'hit', or 'miss'

    # Variables to manage turns
    player_turn = True  # Start with the player's turn

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return 'quit'
        screen.blit(scaled_image, (0, 0))
        if player_turn:
            # Handle player shooting
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button click
                    mouse_x, mouse_y = event.pos
                    # Check if the click is within the computer grid
                    grid_start_x = width - cols * cells_size - 50
                    grid_start_y = 100
                    if grid_start_x <= mouse_x < grid_start_x + cols * cells_size and grid_start_y <= mouse_y < grid_start_y + rows * cells_size:
                        # Calculate grid coordinates
                        col = (mouse_x - grid_start_x) // cells_size
                        row = (mouse_y - grid_start_y) // cells_size

                        # Check if this cell was already clicked
                        if computer_grid_status[row][col] is None:  # If untouched
                            # Determine if it's a hit or miss
                            hit = False
                            for ship in computer_ships:
                                if ship["rect"].collidepoint(
                                        grid_start_x + col * cells_size + cells_size // 2,
                                        grid_start_y + row * cells_size + cells_size // 2
                                ):
                                    computer_grid_status[row][col] = 'hit'
                                    hit = True
                                    break
                            if not hit:
                                computer_grid_status[row][col] = 'miss'

                            # Update the grid status immediately
                            if computer_grid_status[row][col] == 'hit':
                                color = ORANGE  # Orange for hit
                            else:
                                color = PURPLE  # Purple for miss
                            pygame.draw.rect(screen, color, (
                            grid_start_x + col * cells_size, grid_start_y + row * cells_size, cells_size, cells_size))
                            pygame.display.update()

                            # Switch to the computer's turn
                            player_turn = False
        else:
            # Computer's turn
            font = pygame.font.SysFont('Arial', 40)
            thinking_message = font.render("Computer thinking...", True, WHITE)
            screen.blit(thinking_message, (width // 2 - thinking_message.get_width() // 2, 10))
            pygame.display.update()
            time.sleep(2)  # Simulate "thinking" delay
            # Computer shoots randomly
            while True:
                row = random.randint(0, rows - 1)
                col = random.randint(0, cols - 1)
                if player_grid_status[row][col] is None:  # If untouched
                    handle_shooting(row, col, player_grid_status, 50, 100)  # Use handle_shooting to display result
                    pygame.display.update()  # Ensure the grid visually updates
                    break
            # Switch to the player's turn
            player_turn = True

        # Draw grids
        draw_grid_with_labels(50, 100, cells_size, rows, cols)  # Player grid
        draw_grid_with_labels(width - cols * cells_size - 50, 100, cells_size, rows, cols)  # Computer grid

        # Draw player ships
        for ship in player_ships:
            pygame.draw.rect(screen, GREEN, ship["rect"])

        # Draw computer ships (for testing, show them, hide in the actual game)
        for ship in computer_ships:
            pygame.draw.rect(screen, RED, ship["rect"])

        # Draw the status of the grids (hit/miss)
        grid_start_x_computer = width - cols * cells_size - 50
        grid_start_y_computer = 100
        for row in range(rows):
            for col in range(cols):
                # Computer grid
                cell_status = computer_grid_status[row][col]
                if cell_status == 'hit':
                    color = (255, 165, 0)  # Orange for hit
                elif cell_status == 'miss':
                    color = (128, 0, 128)  # Purple for miss
                else:
                    continue
                pygame.draw.rect(screen, color, (grid_start_x_computer + col * cells_size, grid_start_y_computer + row * cells_size, cells_size, cells_size))

                # Player grid
                cell_status = player_grid_status[row][col]
                if cell_status == 'hit':
                    color = ORANGE  # Orange for hit
                elif cell_status == 'miss':
                    color = PURPLE  # Purple for miss
                else:
                    continue
                pygame.draw.rect(screen, color, (50 + col * cells_size, 100 + row * cells_size, cells_size, cells_size))

        # Draw message at the top of the page
        if player_turn:
            message = "Player 1: Shoot one of the grid blocks!"
        else:
            message = "Computer's turn!"
        font = pygame.font.SysFont('Arial', 40)
        message_surface = font.render(message, True, WHITE)
        screen.blit(message_surface, (width // 2 - message_surface.get_width() // 2, 10))
        # Redraw grids and their statuses after each turn
        draw_grid_with_labels(50, 100, cells_size, rows, cols)  # Player grid
        draw_grid_with_labels(width - cols * cells_size - 50, 100, cells_size, rows, cols)  # Computer grid

        # Update the grid statuses visually
        grid_start_x_computer = width - cols * cells_size - 50
        grid_start_y_computer = 100
        for row in range(rows):
            for col in range(cols):
                # Player grid
                cell_status = player_grid_status[row][col]
                if cell_status == "H":
                    color = ORANGE  # Orange for hit
                elif cell_status == "M":
                    color = PURPLE  # Purple for miss
                else:
                    continue
                pygame.draw.rect(screen, color, (50 + col * cells_size, 100 + row * cells_size, cells_size, cells_size))

                # Computer grid
                cell_status = computer_grid_status[row][col]
                if cell_status == "H":
                    color = ORANGE  # Orange for hit
                elif cell_status == "M":
                    color = PURPLE  # Purple for miss
                else:
                    continue
                pygame.draw.rect(screen, color, (
                grid_start_x_computer + col * cells_size, grid_start_y_computer + row * cells_size, cells_size,
                cells_size))
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
    grid_start_x = width - cols * cells_size - 50
    grid_start_y = 100
    grid_width = cols * cells_size
    grid_height = rows * cells_size
    for ship in ships:
        placed = False
        while not placed:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                start_col = random.randint(0, cols - ship["size"])
                start_row = random.randint(0, rows - 1)
                start_x = start_col * cells_size + grid_start_x
                start_y = start_row * cells_size + grid_start_y
                rect = pygame.Rect(start_x, start_y, ship["size"] * cells_size, cells_size)
            else:
                start_col = random.randint(0, cols - 1)
                start_row = random.randint(0, rows - ship["size"])
                start_x = start_col * cells_size + grid_start_x
                start_y = start_row * cells_size + grid_start_y
                rect = pygame.Rect(start_x, start_y, cells_size, ship["size"] * cells_size)
            # Snap to grid
            snapped_x, snapped_y = snap_to_grid(
                rect.x,
                rect.y,
                grid_start_x,
                grid_start_y,
                cells_size,
                grid_width,
                grid_height,
                rect.width,
                rect.height,
            )
            rect.x, rect.y = snapped_x, snapped_y
            # Ensure no overlap
            if not any(r["rect"].colliderect(rect) for r in placed_ships):
                placed_ships.append({"name": ship["name"], "rect": rect, "horizontal": orientation == "horizontal"})
                placed = True
    return placed_ships
def rotate_ship(ship):
    """Rotate the ship between horizontal and vertical."""
    if ship["horizontal"]:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    else:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    ship["horizontal"] = not ship["horizontal"]
def snap_to_grid(x, y, grid_start_x, grid_start_y, cell_size, grid_width, grid_height, ship_width, ship_height):
    """Snap the ship to the nearest grid cell and keep it within bounds."""
    snapped_x = round((x - grid_start_x) / cell_size) * cell_size + grid_start_x
    snapped_y = round((y - grid_start_y) / cell_size) * cell_size + grid_start_y

    # Ensure the ship does not go outside the grid
    if snapped_x + ship_width > grid_start_x + grid_width:
        snapped_x = grid_start_x + grid_width - ship_width
    if snapped_y + ship_height > grid_start_y + grid_height:
        snapped_y = grid_start_y + grid_height - ship_height
    if snapped_x < grid_start_x:
        snapped_x = grid_start_x
    if snapped_y < grid_start_y:
        snapped_y = grid_start_y

    return snapped_x, snapped_y
def handle_shooting(row, col, target_grid, display_x, display_y):
    """Handles shooting logic for a given grid."""
    global current_turn

    # Get the cell coordinates
    x = display_x + col * cells_size
    y = display_y + row * cells_size
    color = PURPLE  # Default to purple for a miss

    if target_grid[row][col] == "S":  # If there's a ship
        color = ORANGE  # Orange for a hit
        target_grid[row][col] = "H"  # Mark as hit
    else:
        target_grid[row][col] = "M"  # Mark as miss

    # Draw the result
    pygame.draw.rect(screen, color, pygame.Rect(x, y, cells_size, cells_size))
    pygame.display.update()

    # Switch turns
    current_turn = "computer" if current_turn == "player" else "player"
def computer_shoot():
    """Handles the computer's turn to shoot."""
    row = random.randint(0, rows - 1)
    col = random.randint(0, cols - 1)

    while pGameLogic[row][col] in ["H", "M"]:  # Avoid already chosen cells
        row = random.randint(0, rows - 1)
        col = random.randint(0, cols - 1)

    handle_shooting(row, col, pGameLogic, 50, 100)  # Player grid position
def player_turn(event):
    """Handles the player's turn based on mouse click."""
    if event.type == pygame.MOUSEBUTTONDOWN and current_turn == "player":
        x, y = event.pos

        # Check if click is within the opponent's grid
        grid_x_start = width - cols * cells_size - 50
        grid_y_start = 100

        if grid_x_start <= x < grid_x_start + cols * cells_size and \
           grid_y_start <= y < grid_y_start + rows * cells_size:
            col = (x - grid_x_start) // cells_size
            row = (y - grid_y_start) // cells_size

            if cGameLogic[row][col] not in ["H", "M"]:  # If not already shot
                handle_shooting(row, col, cGameLogic, grid_x_start, grid_y_start)

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
        draw_button("Start Game", GREEN, start_button)
        draw_button("Settings", (255, 255, 0), settings_button)
        draw_button("Quit", RED, quit_button)

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
                pygame.draw.rect(screen, BLACK, pygame.Rect(cell[0], cell[1], cells_size, cells_size), 1)

        for row in cGameGrid:
            for cell in row:
                pygame.draw.rect(screen, BLACK, pygame.Rect(cell[0], cell[1], cells_size, cells_size), 1)

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
