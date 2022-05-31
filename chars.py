import pygame
import configparser

retrato = pygame.image.load('assets/retrato.png')
retrato_2 = pygame.image.load('assets/retrato_2.png')

class Char(object):
    def __init__(self, name, speed, lifes, image):
        self.name = name
        self.lifes = lifes
        self.speed = speed
        self.image = pygame.image.load(image)


class Characters(object):
    def __init__(self):
        self.chars = {}
        self.size = 0

    def load_file(self, filename="chars.map"):
        parser = configparser.ConfigParser()
        parser.read(filename)
        for section in parser.sections():
            name = section
            speed = parser.get(section, "speed")
            lifes = parser.get(section, "lifes")
            image = parser.get(section, "image")
            char = Char(name, speed, lifes, image)
            self.chars[self.size] = char
            self.size += 1

    def render(self):
        rSize = retrato.get_size()
        r2Size = retrato_2.get_size()

        borderX = 13
        
        surface = pygame.Surface((rSize[0], rSize[1] + r2Size[1] * (self.size - 1)), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        for i in self.chars.keys():
            if i == 0:
                surface.blit(retrato, (0,0))
                surface.blit(self.chars[i].image, (borderX, 7))
            elif i == 1:
                surface.blit(retrato_2, (0,r2Size[1] * i - 1*i))
                surface.blit(self.chars[i].image, (borderX, 3 + r2Size[1] * i))
            else:
                surface.blit(retrato_2, (0,3+r2Size[1] * i - 4*i))
                surface.blit(self.chars[i].image, (borderX, 3+ 4 + r2Size[1] * i - 4*i))

        curr = surface.get_size()
        surface = pygame.transform.scale(surface, (curr[0] * 3.201, curr[1] * 3.2))

        return surface
