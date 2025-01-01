import pygame
import random
import time
from typing import List, Dict, Tuple, Optional

# --- INITIAL SETUP & CONSTANTS ---

pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleships")

# Icon (ensure file "ship.png" is in the working directory)
try:
    icon = pygame.image.load('ship.png')
    pygame.display.set_icon(icon)
except pygame.error:
    pass  # You can optionally handle missing icon by ignoring or logging

background_image = None
try:
    bg_img = pygame.image.load('background.jpeg')  # Ensure "background.jpeg" exists
    background_image = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
except pygame.error:
    pass

# Cells and grid
ROWS = 10
COLS = 10
CELL_SIZE = 33

# Colors
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
RED    = (255, 0, 0)
YELLOW = (255, 255, 0)

# Misc. constants
DEBUG_MODE = False  # True = show computer ships for debugging
ACTIVATION_TIME = 200  # Used for left/right click timing in multiplayer code

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()

# Sound loading
try:
    pew_sound = pygame.mixer.Sound('laser.wav')
    pew_sound.set_volume(0.3)
    collision_sound = pygame.mixer.Sound('collision.wav')
    collision_sound.set_volume(0.55)
    game_over_sound = pygame.mixer.Sound('game_over.wav')
except pygame.error:
    pew_sound = None
    collision_sound = None
    game_over_sound = None

# Title text
title_font = pygame.font.SysFont('Comic Sans MS', 70)
title_text = title_font.render("BattleShips", True, WHITE)
title_rect = title_text.get_rect(center=(WIDTH // 2, 100))

# Global state used for “smart/hard mode” AI
target_stack: List[Tuple[int, int, int, int]] = []
current_direction: Optional[List[int]] = None
ship_orientation: Optional[str] = None
current_ship_cells: List[Tuple[int, int]] = []

# ----------------------------------------------------------------------------
# UTILITY CLASSES AND FUNCTIONS
# ----------------------------------------------------------------------------

def draw_button(text: str, color: Tuple[int, int, int], rect: pygame.Rect):
    """
    Draws a rectangular button and places the given text at the top-left corner.
    """
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.SysFont("Arial", 40)
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (rect.x + 10, rect.y + 10))

def snap_to_grid(x, y, grid_start_x, grid_start_y, cell_size,
                 grid_width, grid_height, ship_width, ship_height):
    """
    Snap a ship's rect to the nearest cell within grid bounds.
    """
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

def rotate_ship(ship: Dict):
    """
    Rotate a ship between horizontal/vertical orientations by swapping its rect width/height.
    """
    if ship["horizontal"]:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    else:
        ship["rect"].width, ship["rect"].height = ship["rect"].height, ship["rect"].width
    ship["horizontal"] = not ship["horizontal"]

def all_ships_sunk(ships: List[Dict]) -> bool:
    """
    Returns True if all ships in the list are marked 'sunk'.
    """
    return all(ship["status"] == "sunk" for ship in ships)

def handle_shooting(row: int, col: int, ships: List[Dict], target_grid: List[List[Optional[str]]],
                    grid_start_x: int, grid_start_y: int) -> bool:
    """
    Mark a shot at (row, col) on the target_grid.
    If it hits one of the ships, mark 'hit' and increment that ship's hit count.
    If the ship is fully hit, mark it as 'sunk'.
    """
    for ship in ships:
        # Convert row/col -> pixel coords for the center of that cell
        if ship["rect"].collidepoint(
            grid_start_x + col * CELL_SIZE + CELL_SIZE // 2,
            grid_start_y + row * CELL_SIZE + CELL_SIZE // 2
        ):
            target_grid[row][col] = "hit"
            ship["hits"] += 1
            if ship["hits"] >= ship["size"]:
                ship["status"] = "sunk"
            return True

    # Otherwise miss
    target_grid[row][col] = "miss"
    return False

def draw_grid_with_labels(x_start: int, y_start: int, cell_size: int,
                          rows: int, cols: int):
    """
    Draw a rows x cols grid with coordinate labels on the left/top edges.
    """
    # Draw the cell rectangles
    for row in range(rows):
        for col in range(cols):
            x = x_start + col * cell_size
            y = y_start + row * cell_size
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, cell_size, cell_size), 1)

    font = pygame.font.SysFont('Arial', 30)
    # Row labels (A-J)
    for i in range(rows):
        label = font.render(chr(65 + i), True, WHITE)  # 65 = 'A'
        screen.blit(label, (x_start - 30, y_start + i * cell_size + 10))

    # Column labels (1-10)
    for j in range(cols):
        label = font.render(str(j + 1), True, WHITE)
        screen.blit(label, (x_start + j * cell_size + 15, y_start - 30))

def draw_grid_status(grid_status: List[List[Optional[str]]],
                     grid_start_x: int, grid_start_y: int):
    """
    Colors each cell in grid_status based on 'hit' or 'miss'.
    """
    for row in range(ROWS):
        for col in range(COLS):
            cell = grid_status[row][col]
            if cell == 'hit':
                color = ORANGE
            elif cell == 'miss':
                color = PURPLE
            else:
                continue  # No color
            pygame.draw.rect(
                screen, color,
                (grid_start_x + col * CELL_SIZE, grid_start_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

def display_game_over(message: str):
    """
    Display a Game Over screen with the specified message.
    """
    font = pygame.font.SysFont('Arial', 80)
    text = font.render(message, True, RED)
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(BLACK)

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.update()
    time.sleep(3)
    pygame.quit()
    exit()

def show_pause_menu():
    """
    Simple pause menu: ESC to resume, Q to quit.
    """
    paused = True
    font = pygame.font.SysFont('Arial', 30)
    pause_text = font.render("Game Paused - Press ESC to Resume or Q to Quit", True, WHITE)
    pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    while paused:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:  # Resume
                    paused = False
                elif ev.key == pygame.K_q:  # Quit
                    pygame.quit()
                    exit()

        screen.fill(BLACK)
        screen.blit(pause_text, pause_rect)
        pygame.display.update()

def credit_menu():
    """
    Shows a simple credits menu. ESC goes back to main menu.
    """
    credits_running = True

    title_font = pygame.font.SysFont('Arial', 50)
    name_font = pygame.font.SysFont('Arial', 30)

    credits_data = [
        {"name": "Youssef Ahmed", "role": "Lead Programmer and Project Manager"},
        {"name": "Marwan Waleed", "role": "Best Contributor"},
        {"name": "Zeyad", "role": "Graphics Designer"},
        {"name": "Hassan", "role": "Debugger and File Control"},
        {"name": "Ammar", "role": "Audio & Sound Manager"},
    ]

    while credits_running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    credits_running = False

        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)

        # Title
        title_text = title_font.render("Credits", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # Names
        start_y = 200
        spacing = 60
        for c in credits_data:
            name_text = name_font.render(f"{c['name']}", True, BLACK)
            role_text = name_font.render(f"{c['role']}", True, (191, 64, 191))
            name_rect = name_text.get_rect(center=(WIDTH // 2, start_y))
            role_rect = role_text.get_rect(center=(WIDTH // 2, start_y + 30))

            screen.blit(name_text, name_rect)
            screen.blit(role_text, role_rect)
            start_y += spacing

        # ESC to go back
        back_text = name_font.render("Press ESC to return to the Main Menu", True, PURPLE)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(back_text, back_rect)
        pygame.display.update()

def display_transition_screen(current_player: int):
    """
    Show a screen telling user to pass the control to the other player.
    """
    screen.fill(BLACK)
    font = pygame.font.SysFont('Arial', 40)
    message = f"Player {current_player}, pass the laptop to Player {3 - current_player}!"
    message_surf = font.render(message, True, WHITE)
    rect = message_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(message_surf, rect)
    pygame.display.update()
    time.sleep(4)

def main_menu():
    """
    Displays the main menu: Start, Settings, Credits, Quit.
    """
    menu_running = True
    while menu_running:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)
        screen.blit(title_text, title_rect)

        # Button definitions
        start_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
        settings_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
        credits_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)
        quit_button = pygame.Rect(WIDTH // 2 - 100, 500, 200, 50)

        # Render them
        draw_button("Start Game", GREEN, start_button)
        draw_button("Settings", YELLOW, settings_button)
        draw_button("Credits", YELLOW, credits_button)
        draw_button("Quit", RED, quit_button)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return 'quit'
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(ev.pos):
                    return 'start'
                elif settings_button.collidepoint(ev.pos):
                    return 'settings'
                elif credits_button.collidepoint(ev.pos):
                    return 'credits'
                elif quit_button.collidepoint(ev.pos):
                    return 'quit'

        pygame.display.update()

def game_mode_menu():
    """
    Asks if user wants Singleplayer or Multiplayer, or back out.
    """
    menu_running = True
    while menu_running:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)
        screen.blit(title_text, title_rect)

        single_button = pygame.Rect(WIDTH // 2 - 150, 200, 300, 50)
        multi_button  = pygame.Rect(WIDTH // 2 - 150, 300, 300, 50)
        back_button   = pygame.Rect(WIDTH // 2 - 150, 400, 300, 50)

        draw_button("Singleplayer", (0, 255, 0), single_button)
        draw_button("Multiplayer" , (0, 255, 255), multi_button)
        draw_button("Back"        , (255, 0, 0)  , back_button)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return 'quit'
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if single_button.collidepoint(ev.pos):
                    return 'singleplayer'
                elif multi_button.collidepoint(ev.pos):
                    return 'multiplayer'
                elif back_button.collidepoint(ev.pos):
                    return 'back'

        pygame.display.update()

def find_nearest_valid_position(selected_ship: Dict, ships: List[Dict]) -> Tuple[int, int]:
    """
    If a ship overlaps or goes out of bounds, find the nearest valid cell to place it.
    """
    valid_positions = []
    grid_start_x = 50
    grid_start_y = 100
    grid_width = COLS * CELL_SIZE
    grid_height = ROWS * CELL_SIZE

    # Generate all possible valid positions
    for row in range(ROWS):
        for col in range(COLS):
            gx = grid_start_x + col * CELL_SIZE
            gy = grid_start_y + row * CELL_SIZE
            # Check bounds
            if gx + selected_ship["rect"].width <= grid_start_x + grid_width and \
               gy + selected_ship["rect"].height <= grid_start_y + grid_height:
                temp_rect = pygame.Rect(gx, gy, selected_ship["rect"].width, selected_ship["rect"].height)
                # Ensure no overlap
                if not any(temp_rect.colliderect(s["rect"]) for s in ships if s != selected_ship):
                    valid_positions.append((gx, gy))

    if not valid_positions:
        return selected_ship["rect"].x, selected_ship["rect"].y

    current_center = selected_ship["rect"].center
    # Find the position with minimal distance
    nearest_position = min(
        valid_positions,
        key=lambda pos: (pos[0] - current_center[0])**2 + (pos[1] - current_center[1])**2
    )
    return nearest_position

def singleplayer_setup(player_count: str, start_next: str):
    """
    Setup screen for singleplayer or multi step. 
    Returns the ship list or 'quit'.
    """
    running = True
    ships = [
        {"name": "Submarine"  , "rect": pygame.Rect(600, 100, CELL_SIZE * 2, CELL_SIZE),
         "horizontal": True, "hits": 0, "size": 2 , "status": "alive", "dragging": False},
        {"name": "Cruiser"    , "rect": pygame.Rect(600, 200, CELL_SIZE * 3, CELL_SIZE),
         "horizontal": True, "hits": 0, "size": 3 , "status": "alive", "dragging": False},
        {"name": "Battleship" , "rect": pygame.Rect(600, 300, CELL_SIZE * 4, CELL_SIZE),
         "horizontal": True, "hits": 0, "size": 4 , "status": "alive", "dragging": False},
        {"name": "Destroyer"  , "rect": pygame.Rect(600, 400, CELL_SIZE * 4, CELL_SIZE),
         "horizontal": True, "hits": 0, "size": 4 , "status": "alive", "dragging": False},
        {"name": "Air Carrier", "rect": pygame.Rect(600, 500, CELL_SIZE * 5, CELL_SIZE),
         "horizontal": True, "hits": 0, "size": 5 , "status": "alive", "dragging": False}
    ]

    selected_ship = None
    all_ships_placed = False
    start_button: Optional[pygame.Rect] = None

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return 'quit'
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    show_pause_menu()
                elif ev.key == pygame.K_q:
                    return 'quit'
                elif ev.key == pygame.K_r and selected_ship:
                    rotate_ship(selected_ship)

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = ev.pos
                if all_ships_placed and start_button and start_button.collidepoint(ev.pos):
                    return ships
                # Check if user clicked on a ship
                for ship in ships:
                    if ship["rect"].collidepoint(mouse_x, mouse_y):
                        ship["dragging"] = True
                        selected_ship = ship
                        break

            elif ev.type == pygame.MOUSEBUTTONUP:
                if selected_ship:
                    selected_ship["dragging"] = False
                    # Snap to grid
                    snap_x, snap_y = snap_to_grid(
                        selected_ship["rect"].x, selected_ship["rect"].y,
                        50, 100, CELL_SIZE, COLS * CELL_SIZE, ROWS * CELL_SIZE,
                        selected_ship["rect"].width, selected_ship["rect"].height
                    )
                    selected_ship["rect"].x, selected_ship["rect"].y = snap_x, snap_y
                    # Check overlap
                    if any(
                        (s != selected_ship and selected_ship["rect"].colliderect(s["rect"]))
                        for s in ships
                    ):
                        n_x, n_y = find_nearest_valid_position(selected_ship, ships)
                        selected_ship["rect"].x, selected_ship["rect"].y = n_x, n_y
                selected_ship = None

        # If a ship is dragging, follow the mouse
        if selected_ship and selected_ship["dragging"]:
            mx, my = pygame.mouse.get_pos()
            selected_ship["rect"].center = (mx, my)

        # Check if all ships are within the grid
        all_ships_placed = all(
            50 <= s["rect"].x < 50 + COLS * CELL_SIZE and
            100 <= s["rect"].y < 100 + ROWS * CELL_SIZE
            for s in ships
        )

        # Drawing
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)
        setup_font = pygame.font.SysFont('Arial', 50)
        setup_text = setup_font.render(f"Player {player_count}: Place Ships", True, WHITE)
        setup_rect = setup_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(setup_text, setup_rect)

        # Draw grid
        draw_grid_with_labels(50, 100, CELL_SIZE, ROWS, COLS)

        # Draw ships
        for sp in ships:
            pygame.draw.rect(screen, GREEN, sp["rect"])
            font = pygame.font.SysFont('Arial', 20)
            label = font.render(sp["name"], True, WHITE)
            screen.blit(label, (sp["rect"].x, sp["rect"].y - 20))

        # If all placed, show the "Start" or "Next" button
        if all_ships_placed:
            start_button = pygame.Rect(WIDTH - 200, HEIGHT - 100, 150, 50)
            draw_button(start_next, GREEN, start_button)

        pygame.display.update()

    return 'quit'

def generate_computer_ships() -> List[Dict]:
    """
    Randomly generates the computer's fleet on the top-right grid.
    """
    # Ship definitions: name & size
    fleet = [
        {"name": "Submarine", "size": 2},
        {"name": "Cruiser", "size": 3},
        {"name": "Battleship", "size": 4},
        {"name": "Destroyer", "size": 4},
        {"name": "Air Carrier", "size": 5},
    ]

    placed_ships = []
    grid_start_x = WIDTH - COLS * CELL_SIZE - 50
    grid_start_y = 100
    grid_width = COLS * CELL_SIZE
    grid_height = ROWS * CELL_SIZE

    for ship in fleet:
        success = False
        while not success:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                start_col = random.randint(0, COLS - ship["size"])
                start_row = random.randint(0, ROWS - 1)
                x_ = start_col * CELL_SIZE + grid_start_x
                y_ = start_row * CELL_SIZE + grid_start_y
                rect = pygame.Rect(x_, y_, ship["size"] * CELL_SIZE, CELL_SIZE)
            else:
                start_col = random.randint(0, COLS - 1)
                start_row = random.randint(0, ROWS - ship["size"])
                x_ = start_col * CELL_SIZE + grid_start_x
                y_ = start_row * CELL_SIZE + grid_start_y
                rect = pygame.Rect(x_, y_, CELL_SIZE, ship["size"] * CELL_SIZE)

            snap_x, snap_y = snap_to_grid(
                rect.x, rect.y,
                grid_start_x, grid_start_y,
                CELL_SIZE, grid_width, grid_height,
                rect.width, rect.height
            )
            rect.x, rect.y = snap_x, snap_y

            # Check overlap
            if not any(r["rect"].colliderect(rect) for r in placed_ships):
                placed_ships.append({
                    "name": ship["name"],
                    "rect": rect,
                    "horizontal": (orientation == "horizontal"),
                    "hits": 0,
                    "size": ship["size"],
                    "status": "alive"
                })
                success = True

    return placed_ships

def draw_game_state(player_ships: List[Dict], computer_grid_status: List[List[Optional[str]]],
                    player_grid_status: List[List[Optional[str]]],
                    player_turn: bool, computer_ships: Optional[List[Dict]] = None,
                    debug_mode: bool = False):
    """
    Draws the two grids, ships, hits/misses, etc.
    """
    # Player grid
    draw_grid_with_labels(50, 100, CELL_SIZE, ROWS, COLS)
    # Computer grid
    right_grid_x = WIDTH - COLS * CELL_SIZE - 50
    draw_grid_with_labels(right_grid_x, 100, CELL_SIZE, ROWS, COLS)

    # Player ships in the left grid
    for sp in player_ships:
        pygame.draw.rect(screen, GREEN, sp["rect"])

    # If debug mode, show computer ships
    if debug_mode and computer_ships:
        for comp_sp in computer_ships:
            pygame.draw.rect(screen, RED, comp_sp["rect"])

    # Draw statuses
    draw_grid_status(computer_grid_status, right_grid_x, 100)
    draw_grid_status(player_grid_status, 50, 100)

    # Info message
    message = "Player's turn: shoot the right grid!" if player_turn else "Computer's turn..."
    font = pygame.font.SysFont('Arial', 40)
    msg_surf = font.render(message, True, WHITE)
    screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 10))

def handle_computer_turn(player_grid_status: List[List[Optional[str]]],
                         player_ships: List[Dict]) -> bool:
    """
    Simple random AI - picks random row/col until it finds an untouched cell.
    """
    # Show a "thinking" message
    font = pygame.font.SysFont('Arial', 40)
    thinking_msg = font.render("Computer thinking...", True, WHITE)
    screen.blit(thinking_msg, (WIDTH // 2 - thinking_msg.get_width() // 2, 10))
    pygame.display.update()
    time.sleep(1.5)

    while True:
        row = random.randint(0, ROWS - 1)
        col = random.randint(0, COLS - 1)
        if player_grid_status[row][col] is None:
            handle_shooting(row, col, player_ships, player_grid_status, 50, 100)
            break

    return True  # Return to player's turn

def singleplayer_hardmode(player_grid_status: List[List[Optional[str]]],
                          player_ships: List[Dict]) -> bool:
    """
    A more advanced AI approach with memory of hits and directions
    (not fully perfect but improved from random).
    """
    global target_stack, current_direction, ship_orientation, current_ship_cells

    def find_adjacent_cells(r: int, c: int):
        """
        Return valid adjacent cells around (r,c) that haven't been shot yet.
        """
        candidates = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            rr, cc = r+dr, c+dc
            if 0 <= rr < ROWS and 0 <= cc < COLS:
                if player_grid_status[rr][cc] is None:
                    candidates.append((rr, cc, dr, dc))
        return candidates

    def choose_target():
        """
        Use target stack and current direction to pick a cell to shoot at.
        Fallback: parity approach, then random if exhausted.
        """
        # If we have a direction, attempt the next cell in that direction
        if current_direction:
            last_r, last_c = current_ship_cells[-1]
            dr, dc = current_direction
            nr, nc = last_r + dr, last_c + dc
            if (0 <= nr < ROWS) and (0 <= nc < COLS) and player_grid_status[nr][nc] is None:
                return (nr, nc, dr, dc)
            else:
                # Reverse direction if out of bounds or cell not valid
                current_direction[0] *= -1
                current_direction[1] *= -1
                return choose_target()

        # Use target_stack if not direction-based
        if target_stack:
            return target_stack.pop()

        # Otherwise, parity approach
        for parity in [(0,0), (1,1)]:
            for row_idx in range(ROWS):
                for col_idx in range(COLS):
                    if (row_idx % 2, col_idx % 2) == parity and player_grid_status[row_idx][col_idx] is None:
                        return (row_idx, col_idx, 0, 0)

        # Fallback random
        for row_idx in range(ROWS):
            for col_idx in range(COLS):
                if player_grid_status[row_idx][col_idx] is None:
                    return (row_idx, col_idx, 0, 0)

        # If nothing left, just fallback
        return (0, 0, 0, 0)

    row, col, dr, dc = choose_target()
    is_hit = handle_shooting(row, col, player_ships, player_grid_status, 50, 100)

    if is_hit:
        current_ship_cells.append((row, col))

        if not current_direction:
            # First hit on this new ship
            adjacent = find_adjacent_cells(row, col)
            # Push them on stack
            for cell in adjacent:
                if cell not in target_stack:
                    target_stack.append(cell)
        else:
            # Continue in direction
            pass
    else:
        # Miss
        current_direction = None
        if len(current_ship_cells) > 1:
            # Check both ends
            start_cell = current_ship_cells[0]
            end_cell = current_ship_cells[-1]
            adj_s = find_adjacent_cells(*start_cell)
            adj_e = find_adjacent_cells(*end_cell)
            for c in adj_s + adj_e:
                if c not in target_stack:
                    target_stack.append(c)
        else:
            # Reset everything
            current_ship_cells.clear()
            ship_orientation = None

    # If a ship just sank, reset direction + memory
    for ship in player_ships:
        if ship["status"] == "alive" and ship["hits"] >= ship["size"]:
            ship["status"] = "sunk"
            current_direction = None
            current_ship_cells.clear()
            ship_orientation = None
            target_stack.clear()
            break

    return True  # Return to player's turn

def start_game_singleplayer(player_ships: List[Dict], difficulty="easy"):
    """
    Main loop for singleplayer.
    """
    running = True
    # Generate computer ships
    computer_ships = generate_computer_ships()

    # Track states
    computer_grid_status = [[None]*COLS for _ in range(ROWS)]
    player_grid_status   = [[None]*COLS for _ in range(ROWS)]

    player_turn = True

    while running:
        # Basic event handling
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    show_pause_menu()
                elif ev.key == pygame.K_q:
                    running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and player_turn:
                # Player's shot
                mx, my = ev.pos
                grid_sx = WIDTH - COLS * CELL_SIZE - 50
                grid_sy = 100
                if (grid_sx <= mx < grid_sx + COLS*CELL_SIZE and
                    grid_sy <= my < grid_sy + ROWS*CELL_SIZE):
                    col = (mx - grid_sx)//CELL_SIZE
                    row = (my - grid_sy)//CELL_SIZE
                    if computer_grid_status[row][col] is None:
                        # Do the shooting
                        is_hit = handle_shooting(row, col, computer_ships, computer_grid_status, grid_sx, grid_sy)
                        player_turn = False  # Switch to computer turn

        # Computer's turn
        if not player_turn:
            if difficulty == "hard":
                player_turn = singleplayer_hardmode(player_grid_status, player_ships)
            else:
                player_turn = handle_computer_turn(player_grid_status, player_ships)

        # Check game over
        if all_ships_sunk(computer_ships):
            display_game_over("Player Wins!")
            break
        elif all_ships_sunk(player_ships):
            display_game_over("Computer Wins!")
            break

        # Draw
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)
        draw_game_state(
            player_ships, computer_grid_status, player_grid_status,
            player_turn, computer_ships, DEBUG_MODE
        )
        pygame.display.update()

def display_transition_screen_multiplayer(current_player: int):
    """
    For multiplayer transitions, simpler wrapper if desired.
    """
    display_transition_screen(current_player)

def start_game_multiplayer(player_ships_p1: List[Dict], player_ships_p2: List[Dict]):
    """
    Multiplayer main loop. Each player tries to shoot on the other's grid.
    """
    running = True
    # Shots are stored as 'hit' or 'miss'
    p1_shots = [[None]*COLS for _ in range(ROWS)]
    p2_shots = [[None]*COLS for _ in range(ROWS)]
    turn = 1

    right_grid_x = WIDTH - COLS * CELL_SIZE - 50
    right_grid_y = 100

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if (right_grid_x <= mx < right_grid_x + COLS*CELL_SIZE and
                    right_grid_y <= my < right_grid_y + ROWS*CELL_SIZE):

                    col = (mx - right_grid_x)//CELL_SIZE
                    row = (my - right_grid_y)//CELL_SIZE

                    # CurrentShots & OpponentShips
                    if turn == 1:
                        current_shots = p1_shots
                        opponent_ships = player_ships_p2
                    else:
                        current_shots = p2_shots
                        opponent_ships = player_ships_p1

                    if current_shots[row][col] is None:
                        # Check if there's a ship
                        hit = False
                        for sp in opponent_ships:
                            # Pixel check
                            if sp["rect"].collidepoint(
                                right_grid_x + col*CELL_SIZE + CELL_SIZE//2,
                                right_grid_y + row*CELL_SIZE + CELL_SIZE//2
                            ):
                                current_shots[row][col] = "hit"
                                hit = True
                                sp["hits"] += 1
                                if sp["hits"] >= sp["size"]:
                                    sp["status"] = "sunk"
                                break
                        if not hit:
                            current_shots[row][col] = "miss"

                        # Next player's turn
                        display_transition_screen_multiplayer(turn)
                        turn = 2 if turn == 1 else 1

        # Drawing
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)

        # Draw left grid (the current player's ships),
        # and right grid is the "firing" grid
        draw_grid_with_labels(50, 100, CELL_SIZE, ROWS, COLS)
        draw_grid_with_labels(right_grid_x, right_grid_y, CELL_SIZE, ROWS, COLS)

        # Show the player's ships on left
        if turn == 1:
            # Player1's ships
            for sp in player_ships_p1:
                pygame.draw.rect(screen, GREEN, sp["rect"])
            # Shots displayed are p1_shots, but those are attempts on p2's grid
            draw_grid_status(p1_shots, right_grid_x, right_grid_y)
        else:
            for sp in player_ships_p2:
                pygame.draw.rect(screen, GREEN, sp["rect"])
            draw_grid_status(p2_shots, right_grid_x, right_grid_y)

        # Info
        font = pygame.font.SysFont('Arial', 30)
        msg = f"Player {turn}'s Turn: Shoot on right grid!"
        msg_surf = font.render(msg, True, WHITE)
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, 10))

        # Check if all ships of one side are sunk
        if all_ships_sunk(player_ships_p1):
            display_game_over("Player 2 Wins!")
            running = False
        elif all_ships_sunk(player_ships_p2):
            display_game_over("Player 1 Wins!")
            running = False

        pygame.display.update()

# ----------------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------------

def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    show_pause_menu()
                elif ev.key == pygame.K_q:
                    running = False

        menu_result = main_menu()

        if menu_result == 'start':
            # Then game mode
            mode_result = game_mode_menu()
            if mode_result == 'singleplayer':
                print("Singleplayer mode selected.")
                # Setup
                player_count = "1"
                start_next = "Start"
                player_ships = singleplayer_setup(player_count, start_next)
                if player_ships != 'quit':
                    # Prompt difficulty (or use a small input from user or define a separate UI)
                    difficulty = input("Choose difficulty: 'easy' or 'hard': ").strip().lower()
                    if difficulty not in ["easy","hard"]:
                        difficulty = "easy"
                    start_game_singleplayer(player_ships, difficulty)
            elif mode_result == 'multiplayer':
                print("Multiplayer selected.")
                # Player1
                p1_count = "1"
                next_btn = "Next"
                ships_p1 = singleplayer_setup(p1_count, next_btn)
                if ships_p1 != 'quit':
                    # Player2
                    p2_count = "2"
                    next_btn = "Start"
                    ships_p2 = singleplayer_setup(p2_count, next_btn)
                    if ships_p2 != 'quit':
                        # Start the actual game
                        start_game_multiplayer(ships_p1, ships_p2)
            elif mode_result == 'back':
                continue
            elif mode_result == 'quit':
                running = False

        elif menu_result == 'settings':
            # Not implemented - add settings logic if needed
            pass
        elif menu_result == 'credits':
            credit_menu()
        elif menu_result == 'quit':
            running = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()

