import pygame


# Initialize pygame
pygame.init()

# create the screen
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
rows = 10
cols = 10
cells_size = 50

# Game Functions
def CreatedGameGrid(rows, cols, cells_size, position):
    start_x = position[0]
    start_y = position[1]
    grid = []
    for row in range(rows):
        row_x=[]
        for col in range(cols):
            row_x.append((start_x , start_y))
            start_x += cells_size
        grid.append(row_x)
        start_x = position[0]
        start_y += cells_size
    return grid
def UPGameLogic(rows, cols):
    #updates game grid space and x with ships
    logic = []
    for row in range(rows):
        row_x=[]
        for col in range(cols):
            row_x.append(" ")
            logic.append(row_x)
        return logic
def printLogic():
    print("Player Grid".center(50, '#'))
    for x in pGameLogic:
        print(x)
    print('Computer Grind'.center(50, '#'))
    for x in cGameLogic:
        print(x)
# Loading Game V
pGameGrid = CreatedGameGrid(rows, cols, cells_size, (50, 50))
pGameLogic = UPGameLogic(rows, cols)

cGameGrid = CreatedGameGrid(rows, cols, cells_size, (width-(rows*cells_size), 50))
cGameLogic = UPGameLogic(rows, cols)

printLogic()

# Title and Icon
pygame.display.set_caption("Battleships")
icon = pygame.image.load('ship.png')
pygame.display.set_icon(icon)

# Game loop
Running = True
while Running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
    # R-G-B
    screen.fill((240, 240, 240))
    pygame.display.update()

pygame.quit()