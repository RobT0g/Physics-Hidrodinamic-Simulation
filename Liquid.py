from audioop import reverse
import enum
from functools import reduce
import math
import pygame
from pygame.locals import *

class Liquid:
    def __init__(self, amount, radius, baseHeight, display):
        try:
            self.disSize = (30*32, 15*32)                   # Dimensões da tela sem a borda (px)
            self.centimeter = 6                             # Razão pixels/cm
            self.holeRadius = 0.008                         # Raio dos furos

            # Líquido
            self.amount = amount                            # Quantidade de líquido (L)
            self.radius = radius/10                         # Raio do recipiente (dm)
            self.height = amount/(3.14*(self.radius**2))    # Altura do volume de líquido inicial (dm)
            self.currentHeight = self.height                # Altura do volume de líquido instantâneo (dm)

            # Base
            self.baseHeight = baseHeight                    # Altura da base em que está o recipiente (cm)
            self.eachHeight = (self.disSize[1]+16, self.disSize[1]+16-(self.baseHeight*self.centimeter))    # Altura do chão e da superficie da base (px)
            self.base = pygame.Surface((self.radius*25*self.centimeter, self.baseHeight*self.centimeter))   
            pygame.draw.rect(self.base, (210, 105, 30), pygame.Rect(0, 0, self.radius*25*self.centimeter, self.baseHeight*self.centimeter))
            pygame.draw.line(self.base, (0, 0, 0), (0, 0), (self.radius*25*self.centimeter, 0))
            pygame.draw.line(self.base, (0, 0, 0), (self.radius*25*self.centimeter-1, 0), (self.radius*25*self.centimeter-1, self.baseHeight*self.centimeter))
            self.holes = [i*(self.height/5) for i in range(1, 5)]                   # Altura dos buracos em relação ao recipiente (dm)
            self.holesHeights = [(i*10 + self.baseHeight)/100 for i in self.holes]  # Altura dos buracos em relação ao chão (m)
            self.times = [math.sqrt(2*i/9.8) for i in self.holesHeights]            # Tempo de caída da altura de um buraco até o chão (s)
            self.updatePressure()
            self.font = pygame.font.SysFont('Times New Roman', 18)
            self.display = display
            self.frame = pygame.image.load('Images\Frame.png')
            self.start = False
            self.finished = False
            self.pause = False
        except:
            self.__init__(20, 10, 10, display)

    def update(self):
        if not self.start or self.finished or self.pause:
            return
        if self.currentHeight > self.holes[0]:
            self.currentHeight -= self.flow
        else:
            self.finished = True
            return
        self.updatePressure()

    def updatePressure(self):
        self.pressures = [101325 + (997*9.8*((self.currentHeight/10)-i) if self.currentHeight*10 > self.holesHeights[k]*100-self.baseHeight else 0) 
            for k, i in enumerate(self.holesHeights)]   # Pressão da água em cada buraco (Pa)
        self.vels = [math.sqrt(2*9.8*((self.currentHeight/10)+(self.baseHeight/100)-v)) if (self.currentHeight/10)+(self.baseHeight/100) >= v else 0 for k, v in enumerate(self.holesHeights)]
        self.flow = 0                                                           # Fluxo de água total (L/s)
        self.reach = [v*self.times[k] for k, v in enumerate(self.vels)]         # Alcance de cada jato (m)
        for i in self.vels:
            self.flow += (self.holeRadius**2)*3.14*i*1000*0.1

    def defineHoles(self, *holes):
        self.holes = []
        for i in holes:
            if i < self.height*10:
                self.holes.append(i/10)
        self.holesHeights = [(i*10 + self.baseHeight)/100 for i in self.holes]
        self.times = [math.sqrt(2*i/9.8) for i in self.holesHeights]
        self.updatePressure()
    
    def defineHoleRad(self, radius):
        self.holeRadius = radius/1000

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
        self.display.blit(txt, (32+length-(0.5*txt.get_size()[0]), self.eachHeight[1]-self.height*self.centimeter*5))
        txt = self.font.render(f'Altura Inicial: {self.height*10:.2f}cm', False, (0, 0, 0))
        pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect((self.radius*self.centimeter*20) + 44, 32, txt.get_size()[0]+6, 62))
        pygame.draw.rect(self.display, (0, 0, 0), pygame.Rect((self.radius*self.centimeter*20) + 44, 32, txt.get_size()[0]+6, 62), 2)
        self.display.blit(txt, ((self.radius*self.centimeter*20) + 47, 32))
        txt = self.font.render(f'Altura atual: {self.currentHeight*10:.2f}cm', False, (0, 0, 0))
        self.display.blit(txt, ((self.radius*self.centimeter*20) + 47, 52))
        txt = self.font.render(f'Vazão: {(self.flow*10):.2f}L/s', False, (0, 0, 0))
        self.display.blit(txt, ((self.radius*self.centimeter*20) + 47, 72))
        txt = self.font.render(' Furo  Press   Vel.  ', False, (0, 0, 0))
        tablesize = (txt.get_size()[0], (len(self.holes)+1)*20)
        tablepos = (self.disSize[0]-txt.get_size()[0]+10, 20)
        table = pygame.Surface(tablesize)
        pygame.draw.rect(table, (255, 255, 255), pygame.Rect(0, 0, txt.get_size()[0], (len(self.holes)+1)*20))
        pygame.draw.rect(table, (0, 0, 0), pygame.Rect(0, 0, txt.get_size()[0], (len(self.holes)+1)*20), 2)
        pygame.draw.line(table, (0, 0, 0), (44, 0), (44, (len(self.holes)+1)*20+20), 2)
        pygame.draw.line(table, (0, 0, 0), (100, 0), (100, (len(self.holes)+1)*20+20), 2)
        self.display.blit(table, tablepos)
        self.display.blit(txt, (self.disSize[0]-txt.get_size()[0]+12, 20))
        for k, v in enumerate(self.holes):
            txt = self.font.render(f'{k+1}', False, (0, 0, 0))
            self.display.blit(txt, (tablepos[0]+5, (k+2)*20))
            txt = self.font.render(f'{self.pressures[(len(self.holes)-1)-k]/1000:.2f}', False, (0, 0, 0))
            self.display.blit(txt, (tablepos[0]+49, (k+2)*20))
            txt = self.font.render(f'{self.vels[(len(self.holes)-1)-k]:.2f}', False, (0, 0, 0))
            self.display.blit(txt, (tablepos[0]+107, (k+2)*20))
            pygame.draw.line(self.display, (0, 0, 0), (tablepos[0], (k+2)*20), (tablepos[0]+tablesize[0], (k+2)*20))
            txt = self.font.render(f'{self.reach[k]*100:.2f}cm', False, (0, 0, 0))
            self.display.blit(txt, ((self.radius*self.centimeter*20) + 36 + self.reach[k]*100*self.centimeter, self.disSize[1]-(20*k)-4))
            pygame.draw.line(self.display, (80, 80, 80), ((self.radius*self.centimeter*20) + 32 + self.reach[k]*100*self.centimeter, self.disSize[1]+15), 
               ((self.radius*self.centimeter*20) + 32 + self.reach[k]*100*self.centimeter, self.disSize[1]-(20*k)-4), 1)

    def drawTrajectories(self):
        for k, v in enumerate(self.reach):
            if v == 0:
                continue
            instr = v*10
            time = self.times[k]/10
            reaches = [i*instr for i in range(11)]
            pos = [(self.radius*self.centimeter*20) + 32, self.eachHeight[1]-(self.holes[k]*self.centimeter*10)]
            vy = 0
            for k1, v1 in enumerate(reaches[:-1]):
                posx = [pos[0] + instr*self.centimeter, pos[1] + (vy*time)*100*self.centimeter + (9.8*(time**2))*100*self.centimeter/2]
                pygame.draw.line(self.display, (156, 211, 219), pos, posx)
                pos = posx[:]
                vy += (9.8*time)

    def putOnScreen(self):
        self.display.blit(self.frame, (0, 0))
        self.display.blit(self.base, (16, self.eachHeight[1]))
        self.display.blit(self.getLiquid(), (32, self.eachHeight[1]-(self.currentHeight*self.centimeter*10-1)))
        self.writeBottle()
        for k, i in enumerate(self.holes):
            pygame.draw.line(self.display, ((156, 211, 219) if self.currentHeight >= i else (38,50,56)), 
                ((self.radius*self.centimeter*20) + 31, self.eachHeight[1]-(i*self.centimeter*10)), 
                ((self.radius*self.centimeter*20) + 33, self.eachHeight[1]-(i*self.centimeter*10)), 3)
        self.drawTrajectories()
        self.showValues()
        pygame.display.flip()
