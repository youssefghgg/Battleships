import pygame
from PIL.ImageOps import scale

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


def singleplayer_setup():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return 'quit'

        # Draw the background
        screen.blit(scaled_image, (0, 0))

        # Display the title text for setup
        setup_font = pygame.font.SysFont('Arial', 50)
        setup_text = setup_font.render("Player 1: Pick Positions", True, (255, 255, 255))
        setup_rect = setup_text.get_rect(center=(width // 2, 50))
        screen.blit(setup_text, setup_rect)

        # Draw the grid
        draw_grid_with_labels(50, 100, cells_size, rows, cols)

        pygame.display.update()

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
            singleplayer_setup()  # Call singleplayer setup
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

    # R-G-B
    screen.blit(scaled_image, (0, 0))
    screen.blit(title_text, title_rect)
    pygame.display.update()


pygame.quit()
