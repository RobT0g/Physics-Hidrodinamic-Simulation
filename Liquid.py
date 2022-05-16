from audioop import reverse
import enum
from functools import reduce
import math
import pygame
from pygame.locals import *

class Liquid:
    def __init__(self, amount, radius, baseHeight, display):
        self.disSize = (30*32, 15*32)                   # Dimensões da tela sem a borda (px)
        self.centimeter = 6                             # Razão pixels/cm

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
        self.updatePressure()
        self.font = pygame.font.SysFont('Times New Roman', 18)
        self.display = display
        self.frame = pygame.image.load('Images\Frame.png')
        self.start = False
    
    def update(self):
        if not self.start:
            return
        if self.currentHeight > self.holes[0]:
            self.currentHeight -= self.flow
        self.updatePressure()

    def updatePressure(self):
        self.times = [math.sqrt(2*i/9.8) for i in self.holesHeights]            # Tempo de caída da altura de um buraco até o chão (s)
        self.pressures = [101325 + 997*9.8*((self.currentHeight/10)-i) for i in self.holesHeights]   # Pressão da água em cada buraco (Pa)
        self.vels = [math.sqrt(2*9.8*((self.currentHeight/10)+(self.baseHeight/100)-v)) if (self.currentHeight/10)+(self.baseHeight/100) >= v else 0 for k, v in enumerate(self.holesHeights)]
        self.flow = 0                                                           # Fluxo de água total (L/s)
        self.reach = [v*self.times[k] for k, v in enumerate(self.vels)]         # Alcance de cada jato (m)
        for i in self.vels:
            self.flow += (0.008**2)*3.14*i*1000*0.1

    def defineHoles(self, *holes):
        self.holes = []
        for i in holes:
            self.holes.append((i-self.baseHeight)/(self.centimeter*10))
        self.holesHeights = [(i*self.centimeter*10 + self.baseHeight)/100 for i in self.holes]
        self.times = [math.sqrt(2*i/9.8) for i in self.holesHeights]

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
        alt = 20
        txt = self.font.render('Altura dos furos', False, (0, 0, 0))
        pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(self.disSize[0]-txt.get_size()[0]-5, alt, txt.get_size()[0]+10, alt*6+2))
        pygame.draw.rect(self.display, (0, 0, 0), pygame.Rect(self.disSize[0]-txt.get_size()[0]-5, alt, txt.get_size()[0]+10, alt*6+2), 1)
        self.display.blit(txt, (self.disSize[0]-txt.get_size()[0], alt))
        for i in self.holesHeights[::-1]:
            alt += 20
            txt = self.font.render(f'{(i*100):.2f}cm', False, (0, 0, 0))
            self.display.blit(txt, (self.disSize[0]-txt.get_size()[0], alt))
        txt = self.font.render(f'Vazão: {(self.flow*10):.2f}L/s', False, (0, 0, 0))
        self.display.blit(txt, (self.disSize[0]-txt.get_size()[0], alt+20))

    def drawTrajectories(self):
        for k, v in enumerate(self.reach):
            if v == 0:
                continue
            instr = v*100/6
            reaches = [i*instr for i in range(int(instr)+1)]
            pos = [(self.radius*self.centimeter*20) + 32, self.eachHeight[1]-(v*10*self.centimeter)]
            vy = 0
            for k1, v1 in enumerate(reaches):
                time = (v1/100-(reaches[k1-1]/100 if k1 != 0 else 0)/self.vels[k])
                posx = [pos[0]+self.vels[k]*time*100*self.centimeter, pos[1]] #+ vy*time*100*self.centimeter + (9.8*time)*100*self.centimeter/2]
                pygame.draw.line(self.display, (156, 211, 219), pos, posx)
                pos = posx[:]
                vy += (9.8*time)/2

    def putOnScreen(self):
        self.display.blit(self.frame, (0, 0))
        self.display.blit(self.base, (16, self.eachHeight[1]))
        self.display.blit(self.getLiquid(), (32, self.eachHeight[1]-(self.currentHeight*self.centimeter*10-1)))
        self.writeBottle()
        for k, i in enumerate(self.holes):
            pygame.draw.line(self.display, ((156, 211, 219) if self.currentHeight >= i else (38,50,56)), 
                ((self.radius*self.centimeter*20) + 31, self.eachHeight[1]-(i*self.centimeter*10)), 
                ((self.radius*self.centimeter*20) + 33, self.eachHeight[1]-(i*self.centimeter*10)), 3)
            #pygame.draw.line(self.display, (156, 211, 219), ((self.radius*self.centimeter*20) + 32, self.eachHeight[1]-i*10*self.centimeter), (self.reach[k]*100*self.centimeter+32+self.radius*20*self.centimeter, self.disSize[1]+16))
        self.drawTrajectories()
        self.showValues()
        pygame.display.flip()
