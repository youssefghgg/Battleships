import pygame
import random
import time

#Initialize pygame
pygame.init()

#Create the screen
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
rows = 10
cols = 10
cells_size = 33
current_turn = "player"
debug_mode = False   # True for showing comp ships, False for playing the game normally
target_stack = []  # Stores cells to check around a hit
current_direction = None  # Direction of exploration after detecting a ship
ship_orientation = None  # Orientation of the ship (horizontal or vertical)
current_ship_cells = []  # Tracks cells of the current target ship

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

#Title and icon
pygame.display.set_caption("Battleships")
icon = pygame.image.load('ship.png')  #Ensure this file exists
pygame.display.set_icon(icon)
background_image = pygame.image.load('background.jpeg')
scaled_image = pygame.transform.scale(background_image,(width,height))
title_font = pygame.font.SysFont('Comic Sans MS', 70)
title_text = title_font.render("BattleShips", True, WHITE)
title_rect = title_text.get_rect(center=(width // 2, 100))
#background_images = [ pygame.image.load('background1.jpg'), pygame.image.load('background2.jpg'), pygame.image.load('background3.jpg') ]

#Game functions
def start_game_multiplayer(player_ships, player_ships2):
    running = True
    player1_shots = [[None for _ in range(cols)] for _ in range(rows)]
    player2_shots = [[None for _ in range(cols)] for _ in range(rows)]
    player_turn = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos


                grid_start_x = width - cols * cells_size - 50
                grid_start_y = 100

                if grid_start_x <= mouse_x < grid_start_x + cols * cells_size and grid_start_y <= mouse_y < grid_start_y + rows * cells_size:
                    col = (mouse_x - grid_start_x) // cells_size
                    row = (mouse_y - grid_start_y) // cells_size

                    current_shots = player1_shots if player_turn == 1 else player2_shots
                    opponent_ships = player_ships2 if player_turn == 1 else player_ships

                    if current_shots[row][col] is None:
                        hit = False
                        for ship in opponent_ships:
                            if ship["rect"].collidepoint(
                                    grid_start_x + col * cells_size + cells_size // 2,
                                    grid_start_y + row * cells_size + cells_size // 2
                            ):
                                current_shots[row][col] = 'hit'
                                hit = True
                                break
                        if not hit:
                            current_shots[row][col] = 'miss'

                        # Transition to the next player
                        display_transition_screen(player_turn)
                        player_turn = 2 if player_turn == 1 else 1

        screen.blit(scaled_image, (0, 0))

        draw_grid_with_labels(50, 100, cells_size, rows, cols)  # Left grid (player ships)
        draw_grid_with_labels(width - cols * cells_size - 50, 100, cells_size, rows, cols)  # Right grid (shared)

        if player_turn == 1:
            for ship in player_ships:
                pygame.draw.rect(screen, GREEN, ship["rect"])
            draw_grid_status(player1_shots, width - cols * cells_size - 50, 100)  # Player 1's shots on right grid
        else:
            for ship in player_ships2:
                pygame.draw.rect(screen, GREEN, ship["rect"])
            draw_grid_status(player2_shots, width - cols * cells_size - 50, 100)  # Player 2's shots on right grid

        font = pygame.font.SysFont('Arial', 30)
        message = f"Player {player_turn}'s Turn: Shoot on the right grid!"
        message_surface = font.render(message, True, WHITE)
        screen.blit(message_surface, (width // 2 - message_surface.get_width() // 2, 10))

        pygame.display.update()
def start_game_singleplayer(player_ships, difficulty="easy"):
    running = True

    # Generate computer ships randomly
    computer_ships = generate_computer_ships()

    # Create grids to track shot status
    computer_grid_status = [[None for _ in range(cols)] for _ in range(rows)]
    player_grid_status = [[None for _ in range(cols)] for _ in range(rows)]

    # Variable to manage turns
    player_turn = True

    while running:
        # Handle all events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Pause the game
                    show_pause_menu()
                elif event.key == pygame.K_q:  # Quit the game
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                # Handle player's mouse click during their turn
                mouse_x, mouse_y = event.pos
                grid_start_x = width - cols * cells_size - 50
                grid_start_y = 100
                if grid_start_x <= mouse_x < grid_start_x + cols * cells_size and grid_start_y <= mouse_y < grid_start_y + rows * cells_size:
                    col = (mouse_x - grid_start_x) // cells_size
                    row = (mouse_y - grid_start_y) // cells_size
                    if computer_grid_status[row][col] is None:  # If untouched
                        handle_shooting(row, col, computer_ships, computer_grid_status, grid_start_x, grid_start_y)
                        player_turn = False  # Switch to computer's turn
                        screen.blit(scaled_image, (0, 0))

        # Update game state
        if not player_turn:
            # Handle computer's turn
            player_turn = handle_computer_turn(player_grid_status, player_ships)
            screen.blit(scaled_image, (0, 0))

        if not player_turn:
            if difficulty == "hard":
                player_turn = singleplayer_hardmode(player_grid_status, player_ships)
            else:
                player_turn = handle_computer_turn(player_grid_status, player_ships)
            screen.blit(scaled_image, (0, 0))

        # Check for game over
        if all_ships_sunk(computer_ships):
            display_game_over("Player Wins!")
            running = False
        elif all_ships_sunk(player_ships):
            display_game_over("Computer Wins!")
            running = False

        # Draw game state
        screen.blit(scaled_image, (0, 0))
        draw_game_state(player_ships, computer_grid_status, player_grid_status, player_turn, computer_ships, debug_mode)
        pygame.display.update()
def singleplayer_hardmode(player_grid_status, player_ships):
    global target_stack, current_direction, ship_orientation, current_ship_cells

    def find_adjacent_cells(row, col):
        """Returns valid adjacent cells."""
        adjacent = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols:  # Check bounds first
                print(f"Cell ({nr}, {nc}) Status: {player_grid_status[nr][nc]}")  # Debugging
                if player_grid_status[nr][nc] is None:
                    adjacent.append((nr, nc, dr, dc))
        return adjacent

    def choose_target():
        """Chooses the next target based on the current state."""
        if current_direction:
            last_row, last_col = current_ship_cells[-1]
            dr, dc = current_direction
            next_row, next_col = last_row + dr, last_col + dc
            if 0 <= next_row < rows and 0 <= next_col < cols and player_grid_status[next_row][next_col] is None:
                return next_row, next_col, dr, dc
            else:
                # Switch to check the other direction
                current_direction[0] *= -1
                current_direction[1] *= -1
                return choose_target()
        elif target_stack:
            print(f"Using target stack: {target_stack}")  # Debugging
            return target_stack.pop()
        else:
            # Random targeting with parity
            print("Falling back to random targeting with parity.")  # Debugging
            for parity in [(0, 0), (1, 1)]:
                for row in range(rows):
                    for col in range(cols):
                        if (row % 2, col % 2) == parity and player_grid_status[row][col] is None:
                            return row, col, 0, 0

            # Fallback in case all parity cells are checked
            for row in range(rows):
                for col in range(cols):
                    if player_grid_status[row][col] is None:
                        return row, col, 0, 0

    # Choose a target
    row, col, dr, dc = choose_target()
    hit = handle_shooting(row, col, player_ships, player_grid_status, 50, 100)

    if hit:
        print(f"HIT detected at ({row}, {col})")  # Debugging
        current_ship_cells.append((row, col))

        if not current_direction:
            # First hit: Populate adjacent cells
            adjacent = find_adjacent_cells(row, col)
            target_stack.extend(cell for cell in adjacent if cell[:2] not in target_stack)
            print(f"Target stack after hit: {target_stack}")  # Debugging
        else:
            # Continue in the current direction
            next_row, next_col = row + dr, col + dc
            if 0 <= next_row < rows and 0 <= next_col < cols and player_grid_status[next_row][next_col] is None:
                target_stack.append((next_row, next_col, dr, dc))
    else:
        print(f"MISS at ({row}, {col})")  # Debugging
        current_direction = None
        if len(current_ship_cells) > 1:
            # Check both ends of the ship
            start_cell = current_ship_cells[0]
            end_cell = current_ship_cells[-1]
            adjacent = find_adjacent_cells(*start_cell) + find_adjacent_cells(*end_cell)
            target_stack.extend(cell for cell in adjacent if cell[:2] not in target_stack)
        else:
            # Reset for new target
            current_ship_cells.clear()
            ship_orientation = None

    # If the current ship sinks, reset for the next target
    for ship in player_ships:
        if ship["status"] == "alive" and ship["hits"] >= ship["size"]:
            ship["status"] = "sunk"
            current_direction = None
            current_ship_cells.clear()
            ship_orientation = None
            target_stack.clear()
            break

    return True  # Return control to the player
def created_game_grid(rows, cols, cells_size, position):
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
def up_game_logic(rows, cols):
    #Updates game grid space and x with ships
    logic = []
    for row in range(rows):
        row_x = []
        for col in range(cols):
            row_x.append(" ")
            logic.append(row_x)
    return logic
def draw_grid_with_labels(x_start, y_start, cell_size, rows, cols):
    #Draw the grid
    for row in range(rows):
        for col in range(cols):
            x = x_start + col * cell_size
            y = y_start + row * cell_size
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, cell_size, cell_size), 1)

    #Draw row labels (A-J)
    font = pygame.font.SysFont('Arial', 30)
    for i in range(rows):
        label = font.render(chr(65 + i), True, WHITE)  # A=65 in ASCII
        screen.blit(label, (x_start - 30, y_start + i * cell_size + 10))

    #Draw column labels (1-10)
    for j in range(cols):
        label = font.render(str(j + 1), True, WHITE)
        screen.blit(label, (x_start + j * cell_size + 15, y_start - 30))
def snap_to_grid(x, y, grid_start_x, grid_start_y, cell_size, grid_width, grid_height, ship_width, ship_height):
    #Snap the ship to the nearest valid grid cell
    snapped_x = round((x - grid_start_x) / cell_size) * cell_size + grid_start_x
    snapped_y = round((y - grid_start_y) / cell_size) * cell_size + grid_start_y

    #Ensure the ship stays within the grid boundaries
    if snapped_x + ship_width > grid_start_x + grid_width:
        snapped_x = grid_start_x + grid_width - ship_width
    if snapped_y + ship_height > grid_start_y + grid_height:
        snapped_y = grid_start_y + grid_height - ship_height
    if snapped_x < grid_start_x:
        snapped_x = grid_start_x
    if snapped_y < grid_start_y:
        snapped_y = grid_start_y

    return snapped_x, snapped_y
def game_mode_menu() -> object:
    menu_running = True
    while menu_running:
        #Draw the background first
        screen.blit(scaled_image, (0, 0))
        screen.blit(title_text, title_rect)

        #Define button rectangles
        singleplayer_button = pygame.Rect(width // 2 - 150, 200, 300, 50)
        multiplayer_button = pygame.Rect(width // 2 - 150, 300, 300, 50)
        back_button = pygame.Rect(width // 2 - 150, 400, 300, 50)

        #Draw buttons
        draw_button("Singleplayer", (0, 255, 0), singleplayer_button)
        draw_button("Multiplayer", (0, 255, 255), multiplayer_button)
        draw_button("Back", (255, 0, 0), back_button)

        #Check for events
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
def singleplayer_setup():
    running = True

    ships = [
        {"name": "Submarine", "rect": pygame.Rect(600, 100, cells_size * 2, cells_size), "horizontal": True, "hits": 0,
         "size": 2, "status": "alive"},
        {"name": "Cruiser", "rect": pygame.Rect(600, 200, cells_size * 3, cells_size), "horizontal": True, "hits": 0,
         "size": 3, "status": "alive"},
        {"name": "Battleship", "rect": pygame.Rect(600, 300, cells_size * 4, cells_size), "horizontal": True, "hits": 0,
         "size": 4, "status": "alive"},
        {"name": "Destroyer", "rect": pygame.Rect(600, 400, cells_size * 4, cells_size), "horizontal": True, "hits": 0,
         "size": 4, "status": "alive"},
        {"name": "Air Carrier", "rect": pygame.Rect(600, 500, cells_size * 5, cells_size), "horizontal": True,
         "hits": 0, "size": 5, "status": "alive"}
    ]

    selected_ship = None
    all_ships_placed = False
    start_button = None

    while running:
        for event in pygame.event.get():


            if event.type == pygame.MOUSEBUTTONDOWN:
                if all_ships_placed and start_button and start_button.collidepoint(event.pos):
                    return ships  #Return the player's ship positions
                for ship in ships:
                    if ship["rect"].collidepoint(event.pos):
                        ship["dragging"] = True
                        selected_ship = ship
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_ship:
                    selected_ship["dragging"] = False
                    #Snap to grid with boundary checks
                    snapped_x, snapped_y = snap_to_grid(
                        selected_ship["rect"].x,
                        selected_ship["rect"].y,
                        50,  #Grid start x
                        100,  #Grid start y
                        cells_size,  #Cell size
                        cols * cells_size,  #Grid width
                        rows * cells_size,  #Grid height
                        selected_ship["rect"].width,  #Ship width
                        selected_ship["rect"].height,  #Ship height
                    )
                    #Set snapped position
                    selected_ship["rect"].x, selected_ship["rect"].y = snapped_x, snapped_y
                    #Check for overlap and resolve it
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
        setup_text = setup_font.render(f"Player {player_count}: Pick Positions", True, WHITE)
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
            draw_button(f"{start_next}", GREEN, start_button)
        pygame.display.update()
def find_nearest_valid_position(selected_ship, ships):
    valid_positions = []

    for row in range(rows):
        for col in range(cols):
            grid_x = 50 + col * cells_size
            grid_y = 100 + row * cells_size

            #Ensure the ship fits within the grid boundaries
            if grid_x + selected_ship["rect"].width <= 50 + cols * cells_size and \
               grid_y + selected_ship["rect"].height <= 100 + rows * cells_size:

                #Create a temp rect for collision checking
                temp_rect = pygame.Rect(grid_x, grid_y, selected_ship["rect"].width, selected_ship["rect"].height)

                #Ensure no overlap with other ships
                if not any(temp_rect.colliderect(ship["rect"]) for ship in ships if ship != selected_ship):
                    valid_positions.append((grid_x, grid_y))

    #Find the closest valid posi]tion
    current_center = selected_ship["rect"].center
    nearest_position = min(valid_positions, key=lambda pos: (pos[0] - current_center[0])*2 + (pos[1] - current_center[1])*2)
    return nearest_position
def handle_player_turn(computer_ships, computer_grid_status):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            grid_start_x = width - cols * cells_size - 50
            grid_start_y = 100

            if grid_start_x <= mouse_x < grid_start_x + cols * cells_size and grid_start_y <= mouse_y < grid_start_y + rows * cells_size:
                col = (mouse_x - grid_start_x) // cells_size
                row = (mouse_y - grid_start_y) // cells_size

                if computer_grid_status[row][col] is None:
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

                    color = ORANGE if computer_grid_status[row][col] == 'hit' else PURPLE
                    pygame.draw.rect(screen, color, (
                        grid_start_x + col * cells_size, grid_start_y + row * cells_size, cells_size, cells_size
                    ))
                    return False  # Switch to computer's turn
    return True  # Stay on player's turn
def handle_computer_turn(player_grid_status, player_ships):
    font = pygame.font.SysFont('Arial', 40)
    thinking_message = font.render("Computer thinking...", True, WHITE)
    screen.blit(thinking_message, (width // 2 - thinking_message.get_width() // 2, 10))
    pygame.display.update()
    time.sleep(2)  # Simulate thinking delay

    while True:
        row = random.randint(0, rows - 1)
        col = random.randint(0, cols - 1)
        if player_grid_status[row][col] is None:  # If untouched
            handle_shooting(row, col, player_ships, player_grid_status, 50, 100)  # Pass player_ships
            break

    return True  # Switch back to player's turn
def draw_game_state(player_ships, computer_grid_status, player_grid_status, player_turn, computer_ships=None, debug_mode=False):
    draw_grid_with_labels(50, 100, cells_size, rows, cols)  # Player grid
    draw_grid_with_labels(width - cols * cells_size - 50, 100, cells_size, rows, cols)  # Computer grid

    # Draw player ships
    for ship in player_ships:
        pygame.draw.rect(screen, GREEN, ship["rect"])

    # Draw computer ships if debug mode is enabled
    if debug_mode and computer_ships:
        for ship in computer_ships:
            pygame.draw.rect(screen, RED, ship["rect"])

    # Draw grid statuses
    draw_grid_status(computer_grid_status, width - cols * cells_size - 50, 100)  # Computer grid
    draw_grid_status(player_grid_status, 50, 100)  # Player grid

    # Draw message at the top of the screen
    message = "Player 1: Shoot one of the grid blocks!" if player_turn else "Computer's turn!"
    font = pygame.font.SysFont('Arial', 40)
    message_surface = font.render(message, True, WHITE)
    screen.blit(message_surface, (width // 2 - message_surface.get_width() // 2, 10))
def draw_grid_status(grid_status, grid_start_x, grid_start_y):
    for row in range(rows):
        for col in range(cols):
            cell_status = grid_status[row][col]
            if cell_status == 'hit':
                color = ORANGE  # Orange for hit
            elif cell_status == 'miss':
                color = PURPLE  # Purple for miss
            else:
                continue
            pygame.draw.rect(screen, color, (
                grid_start_x + col * cells_size, grid_start_y + row * cells_size, cells_size, cells_size
            ))
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

            snapped_x, snapped_y = snap_to_grid(
                rect.x, rect.y, grid_start_x, grid_start_y, cells_size, grid_width, grid_height, rect.width, rect.height
            )
            rect.x, rect.y = snapped_x, snapped_y

            # Ensure no overlap
            if not any(r["rect"].colliderect(rect) for r in placed_ships):
                placed_ships.append({
                    "name": ship["name"],
                    "rect": rect,
                    "horizontal": orientation == "horizontal",
                    "hits": 0,
                    "size": ship["size"],
                    "status": "alive"  # Add the status field
                })
                placed = True
    return placed_ships

    pygame.display.update()
def rotate_ship(ship):
    #Rotate the ship between horizontal and vertical
    if ship["horizontal"]:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    else:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    ship["horizontal"] = not ship["horizontal"]
def handle_shooting(row, col, ships, target_grid, grid_start_x, grid_start_y):
    # Check if the shot hits a ship
    for ship in ships:
        if ship["rect"].collidepoint(
            grid_start_x + col * cells_size + cells_size // 2,
            grid_start_y + row * cells_size + cells_size // 2
        ):
            target_grid[row][col] = "hit"
            ship["hits"] += 1
            if ship["hits"] >= ship["size"]:  # Check if the ship is sunk
                ship["status"] = "sunk"
                print(f"{ship['name']} is sunk!")  # Debug message
            return True  # Hit

    # If no ship is hit, mark as miss
    target_grid[row][col] = "miss"
    return False
def all_ships_sunk(ships):
    return all(ship["status"] == "sunk" for ship in ships)

def display_transition_screen(current_player):
    screen.fill(BLACK)
    font = pygame.font.SysFont('Arial', 40)
    message = f"Player {current_player}, pass the laptop to Player {3 - current_player}!"
    message_surface = font.render(message, True, WHITE)
    screen.blit(message_surface, (width // 2 - message_surface.get_width() // 2, height // 2))
    pygame.display.update()
    time.sleep(4)
def display_game_over(message):
    font = pygame.font.SysFont('Arial', 80)
    text = font.render(message, True, RED)
    screen.blit(scaled_image, (0, 0))
    screen.blit(text, text.get_rect(center=(width // 2, height // 2)))
    pygame.display.update()
    time.sleep(3)
    pygame.quit()
    exit()



#Loading game
pGameGrid = created_game_grid(rows, cols, cells_size, (50, 50))
pGameLogic = up_game_logic(rows, cols)

cGameGrid = created_game_grid(rows, cols, cells_size, (width - (rows * cells_size), 50))
cGameLogic = up_game_logic(rows, cols)

#Menu functions
def draw_button(text, color, rect):
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.SysFont("Arial", 40)
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (rect.x + 10, rect.y + 10))
def main_menu():
    menu_running = True
    while menu_running:
        #Draw the background first
        screen.blit(scaled_image, (0, 0))
        screen.blit(title_text, title_rect)

        #Define button rectangles
        start_button = pygame.Rect(width // 2 - 100, 200, 200, 50)
        settings_button = pygame.Rect(width // 2 - 100, 300, 200, 50)
        credits_button = pygame.Rect(width // 2 - 100, 400, 200, 50)
        quit_button = pygame.Rect(width // 2 - 100, 500, 200, 50)

        #Draw buttons
        draw_button("Start Game", GREEN, start_button)
        draw_button("Settings", YELLOW, settings_button)
        draw_button("Credits" , YELLOW , credits_button)
        draw_button("Quit", RED, quit_button)

        #Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return 'start'
                elif settings_button.collidepoint(event.pos):
                    return 'settings'
                elif credits_button.collidepoint(event.pos):
                    return 'credits'
                elif quit_button.collidepoint(event.pos):
                    return 'quit'

        pygame.display.update()
def show_pause_menu():
    paused = True
    font = pygame.font.SysFont('Arial', 30)
    resume_text = font.render("Game Paused - Press ESC to Resume or Q to Quit", True, WHITE)
    resume_rect = resume_text.get_rect(center=(width // 2, height // 2))

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Resume on ESC
                    paused = False
                elif event.key == pygame.K_q:  # Quit on Q
                    pygame.quit()
                    exit()

        # Display the pause menu
        screen.fill(BLACK)
        screen.blit(resume_text, resume_rect)
        pygame.display.update()
def credit_menu():
    # Flag to keep the credits menu running
    credits_running = True

    # Font setup
    title_font = pygame.font.SysFont('Arial', 50)
    name_font = pygame.font.SysFont('Arial', 30)

    # Credits data
    credits = [
        {"name": "Youssef Ahmed", "role": "Lead Programmer and Project Manager"},
        {"name": "Marwan Waleed", "role": "Best contributor"},
        {"name": "Zeyad", "role": "Graphics Designer"},
        {"name": "Hassan", "role": "Debugger and File control"},
        {"name": "Ammar", "role": "Audio and Sound Manager"},
    ]

    while credits_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Go back to the main menu on ESC
                    credits_running = False

        # Draw the background
        screen.blit(scaled_image, (0, 0))

        # Draw title
        title_text = title_font.render("Credits", True, WHITE)
        title_rect = title_text.get_rect(center=(width // 2, 100))
        screen.blit(title_text, title_rect)

        # Display each person's name and role
        start_y = 200  # Starting y-coordinate for names
        spacing = 60   # Spacing between each name and role
        for credit in credits:
            name_text = name_font.render(f"{credit['name']}", True, BLACK)
            role_text = name_font.render(f"{credit['role']}", True, (191, 64, 191) )

            name_rect = name_text.get_rect(center=(width // 2, start_y))
            role_rect = role_text.get_rect(center=(width // 2, start_y + 30))

            screen.blit(name_text, name_rect)
            screen.blit(role_text, role_rect)

            start_y += spacing

        # Instruction to go back
        back_text = name_font.render("Press ESC to return to the Main Menu", True, PURPLE)
        back_rect = back_text.get_rect(center=(width // 2, height - 50))
        screen.blit(back_text, back_rect)

        pygame.display.update()


#Main flow
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Pause on ESC
                show_pause_menu()
            elif event.key == pygame.K_q:  # Quit on Q
                running = False

    menu_result = main_menu()
    if menu_result == 'start':
        mode_result = game_mode_menu()  # Open game mode menu
        if mode_result == 'singleplayer':
            print("Singleplayer mode selected")
            player_count = "1"
            start_next = "Start"
            player_ships = singleplayer_setup()
            if player_ships != 'quit':
                # Choose difficulty
                difficulty = input("Choose difficulty: 'easy' or 'hard': ").strip().lower()
                if difficulty not in ["easy", "hard"]:
                    difficulty = "easy"  # Default to easy if input is invalid

                # Start singleplayer game with the chosen difficulty
                start_game_singleplayer(player_ships, difficulty=difficulty)
        elif mode_result == 'multiplayer':
            print("Multiplayer mode selected")
            player_count = "1"
            start_next = "Next"
            player_ships = singleplayer_setup()  # Call singleplayer setup
            if player_ships != 'quit':  # If the user doesnt quit start the game
                player_count = "2"
                start_next = "Start"
                player_ships2 = singleplayer_setup()
                start_game_multiplayer(player_ships, player_ships2)
                if player_ships2 != 'quit':
                    pass
                    # multiplay(player_ships, player_ships2)
        elif mode_result == 'back':
            continue  # Return to the main menu
        elif mode_result == 'quit':
            running = False
    elif menu_result == 'quit':
        running = False
    # elif menu_result == 'settings':
        pass  # Add settings handling if needed
    elif menu_result == 'credits':
        credit_menu()
        
    pygame.display.update()

pygame.quit()
