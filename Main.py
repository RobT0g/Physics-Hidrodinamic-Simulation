import pygame
from pygame.locals import *
from Liquid import Liquid

pygame.init()                                                           # inicialização

screen_width = 31*32                                                    # largura da tela
screen_height = 16*32                                                   # altura da tela

display = pygame.display.set_mode((screen_width, screen_height))        # tela definida
pygame.display.set_caption('Hidrodinamics')                             # legenda da tela
liq = Liquid(15, 10, 15, display)
liq.putOnScreen()

running = True                      # Variável de looping
while running:                      # looping
    for e in pygame.event.get():
        if e.type == pygame.MOUSEBUTTONDOWN:
            liq.currentHeight = 3
            liq.putOnScreen()
        if pygame.key.get_pressed()[pygame.K_ESCAPE] or e.type == QUIT:
            running = False