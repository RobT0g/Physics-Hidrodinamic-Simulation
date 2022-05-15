from sys import displayhook
import pygame
from pygame.locals import *

class Liquid:
    def __init__(self, amount, radius, baseHeight, display):
        self.disSize = (30*32, 15*32)
        self.centimeter = 6

        # Líquido
        self.amount = amount 
        self.radius = radius/10
        self.height = amount/(3.14*(self.radius**2))
        self.currentHeight = self.height

        # Base
        self.baseHeight = baseHeight
        self.eachHeight = (self.disSize[1]+16, self.disSize[1]+16-(self.baseHeight*self.centimeter))
        self.base = pygame.Surface((self.radius*25*self.centimeter, self.baseHeight*self.centimeter))
        pygame.draw.rect(self.base, (210, 105, 30), pygame.Rect(0, 0, self.radius*25*self.centimeter, self.baseHeight*self.centimeter))
        pygame.draw.line(self.base, (0, 0, 0), (0, 0), (self.radius*25*self.centimeter, 0))
        pygame.draw.line(self.base, (0, 0, 0), (self.radius*25*self.centimeter-1, 0), (self.radius*25*self.centimeter-1, self.baseHeight*self.centimeter))
        
        self.holes = [i*(self.height/5) for i in range(1, 5)]
        self.font = pygame.font.SysFont('Times New Roman', 18)
        self.display = display
        self.frame = pygame.image.load('Images\Frame.png')
        self.start = False

    def defineHoles(self, *holes):
        self.holes = holes

    def getLiquid(self):
        a = pygame.Surface((self.radius*self.centimeter*20 + 2, self.currentHeight*self.centimeter*10))
        pygame.draw.rect(a, (156, 211, 219), pygame.Rect(1, 0, self.radius*self.centimeter*20, self.currentHeight*self.centimeter*10))
        return a
    
    def writeBottle(self):
        pygame.draw.line(self.display, (0, 0, 0), (32, (self.eachHeight[1]-self.height*self.centimeter*10)-16), (32, self.eachHeight[1]), 3)
        pygame.draw.line(self.display, (0, 0, 0), ((self.radius*self.centimeter*20) + 32, (self.eachHeight[1]-self.height*self.centimeter*10)-16), ((self.radius*self.centimeter*20) + 32, self.eachHeight[1]), 3)

    def showValues(self):
        length = self.radius*self.centimeter*10
        label = pygame.Surface((length, 25))
        pygame.draw.rect(label, (255, 255, 255), pygame.Rect(0, 0, length, 25))
        self.display.blit(label, (32+(0.5*length), self.eachHeight[1]-self.height*self.centimeter*5))
        amount = (self.radius**2)*3.14*self.currentHeight
        txt = self.font.render(f'{amount:.2f} L', False, (0, 0, 0))
        self.display.blit(txt, (32+(txt.get_size()[0]/2), self.eachHeight[1]-self.height*self.centimeter*5))

    def putOnScreen(self):
        self.display.blit(self.frame, (0, 0))
        self.display.blit(self.base, (16, self.eachHeight[1]))
        self.display.blit(self.getLiquid(), (32, self.eachHeight[1]-(self.currentHeight*self.centimeter*10-1)))
        self.writeBottle()
        for i in self.holes:
            pygame.draw.line(self.display, ((156, 211, 219) if self.currentHeight >= i else (38,50,56)), 
                ((self.radius*self.centimeter*20) + 31, self.eachHeight[1]-(i*self.centimeter*10)), 
                ((self.radius*self.centimeter*20) + 33, self.eachHeight[1]-(i*self.centimeter*10)), 3)
        self.showValues()
        pygame.display.flip()
