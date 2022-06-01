import pygame
import configparser

retrato = pygame.image.load('assets/retrato.png')
retrato_2 = pygame.image.load('assets/retrato_2.png')

lifebar = pygame.image.load('assets/lifebar/lifebar_0.png')
lifebar_2 = pygame.image.load('assets/lifebar/lifebar_1.png')

fill_first = pygame.image.load('assets/lifebar/fill_first.png')
fill_last = pygame.image.load('assets/lifebar/fill_last.png')
fill_middle = pygame.image.load('assets/lifebar/fill_middle.png')

class Char(object):
    def __init__(self, name, speed, life, image):
        self.name = name
        self.maxLife = life
        self.currLife = life
        self.speed = speed
        self.image = pygame.image.load(image)
    
    def useChar(self):
        self.currLife -= 1
    
    def render(self, first = True):
        curr = retrato if first else retrato_2
        rSize = curr.get_size()

        borderX = 13
        surface = pygame.Surface((rSize[0] + borderX * self.maxLife, rSize[1]), pygame.SRCALPHA, 32)

        surface.blit(curr, (borderX * self.maxLife,0))
        surface.blit(self.image, (borderX * (self.maxLife+1), 7 if first else 4))

        surface.blit(lifebar, (borderX * (self.maxLife-1), 21 if first else 18))
        for i in range(1, self.maxLife):
            surface.blit(lifebar_2, ((borderX-2) * (self.maxLife-i) + 3 + 5 * i,21 if first else 18))

        if self.currLife > 0:
            surface.blit(fill_first, (97, 27 if first else 24))
            for i in range(1, self.currLife):
                surface.blit(fill_middle, (97 - 6*i, 27 if first else 24))
            if self.currLife == self.maxLife:
                surface.blit(fill_last, (97 - 6*(self.currLife-1), 27 if first else 24))

        return surface


class Characters(object):
    def __init__(self):
        self.chars = {}
        self.size = 0

        self.solPosition = {}
        self.etapas = []

    def load_file(self, filename="chars.map"):
        parser = configparser.ConfigParser()
        parser.read(filename)
        for section in parser.sections():
            if section != "Etapas":
                name = section
                speed = float(parser.get(section, "speed"))
                lifes = int(parser.get(section, "lifes"))
                image = parser.get(section, "image")
                char = Char(name, speed, lifes, image)
                self.chars[name] = char
                self.size += 1
        
        sols = open(parser.get("Etapas", "solution"), 'r')
        sols = sols.read().split("\n")
        for i in range(self.size):
            self.solPosition[i] = sols[i]
        
        for etapa in sols[self.size:]:
            self.etapas.append([int(x) for x in etapa.split(" ")])

    def solucionarEtapa(self, etapa):
        for i in range(len(self.etapas[etapa])):
            if self.etapas[etapa][i] == 1:
                char = self.solPosition[i]
                self.chars[char].useChar()


    def render(self):
        rSize = retrato.get_size()
        r2Size = retrato_2.get_size()

        borderX = 13
        
        surface = pygame.Surface((rSize[0] + borderX * 8, rSize[1] + r2Size[1] * (self.size - 1)), pygame.SRCALPHA, 32)
        for idx, i in enumerate(self.chars.keys()):
            char = self.chars[i].render(idx == 0)
            if i == 0:
                surface.blit(char, (0, 0))
            elif i == 1:
                surface.blit(char, (0, char.get_size()[1] - 1))
            else:
                surface.blit(char, (0, char.get_size()[1] * idx - 4 * idx + 3))

        curr = surface.get_size()
        surface = pygame.transform.scale(surface, (curr[0] * 3.2, curr[1] * 3.2))

        return surface
