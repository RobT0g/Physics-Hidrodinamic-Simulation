import pygame
from pygame.locals import *
from Liquid import Liquid

pygame.init()                                                           # inicialização

screen_width = 31*32                                                    # largura da tela
screen_height = 16*32                                                   # altura da tela

refresh = 100
clock = pygame.time.Clock() 
update = pygame.USEREVENT + 1
pygame.time.set_timer(update, refresh)

display = pygame.display.set_mode((screen_width, screen_height))        # tela definida
pygame.display.set_caption('Hidrodinamics')   
liqSpec = (20, 10, 10, display)    #amount, radius, baseHeight, display 
liq = Liquid(*liqSpec)
liq.putOnScreen()

running = True                      # Variável de looping
while running:                      # looping
    for e in pygame.event.get():
        if e.type == update:
            liq.update()
            liq.putOnScreen()
        if e.type == pygame.MOUSEBUTTONDOWN:
            liq.start = True
            if liq.finished:
                liq = Liquid(*liqSpec)
        if pygame.key.get_pressed()[pygame.K_ESCAPE] or e.type == QUIT:
            running = False