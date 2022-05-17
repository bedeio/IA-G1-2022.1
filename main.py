import pygame
import pygame.locals
from pygame.locals import *
import configparser


class Level(object):
    def load_file(self, filename="level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read(filename)
        map = open(parser.get("level", "map"), 'r')
        self.map = map.read().split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.setStageList()

    def render(self):
        image = pygame.Surface(
            (self.width*MAP_TILE_WIDTH, self.height*MAP_TILE_HEIGHT))
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                red, green, blue = 0, 0, 0
                color = ''
                if c in self.key.keys():
                    color = self.key[c]['color']
                else:
                    color = self.key['_']['color']
                red, green, blue = [int(v) for v in color.split(',')]
                rect = pygame.Surface((MAP_TILE_WIDTH, MAP_TILE_HEIGHT))
                rect.fill((red, green, blue))
                image.blit(rect,
                           (map_x*MAP_TILE_WIDTH, map_y*MAP_TILE_HEIGHT))
        return image
    
    def setStageList(self):
        self.stages = []
        for line in range(self.height):
            lineObjs = set(self.map[line])
            for letter in lineObjs:
                if letter not in self.key.keys():
                    col = self.map[line].find(letter)
                    self.stages.append([col, line, letter])

        self.stages.sort(key = lambda x: x[2])


if __name__ == "__main__":
    screen = pygame.display.set_mode((1000, 600))

    MAP_TILE_WIDTH = 3
    MAP_TILE_HEIGHT = 6

    level = Level()
    level.load_file('map/level.map')

    clock = pygame.time.Clock()

    background = level.render()
    overlays = pygame.sprite.RenderUpdates()
    screen.blit(background, (0, 0))

    overlays.draw(screen)
    pygame.display.flip()

    game_over = False

    while not game_over:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_over = True

        overlays.draw(screen)
        pygame.display.flip()
        clock.tick(15)
