import pygame


# Initialize pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((800, 600))

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
    screen.fill((0, 0, 0))
    pygame.display.update()
