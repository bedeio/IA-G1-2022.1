import pygame
import pygame.locals
from pygame.locals import *
import configparser
import threading
import time
import math
from queue import PriorityQueue
from chars import Characters


class Level(object):
    def __init__(self):
        self.stages = []
        self.map = []
        self.key = {}
        self.width = 0
        self.height = 0

        self.currStage = 0
        self.running = False

        # a* state
        self.open_q = PriorityQueue()
        self.open_lst = []
        self.reconst_path = []

    def load_file(self, filename="level.map"):
        parser = configparser.ConfigParser()
        parser.read(filename)
        map = open(parser.get("level", "map"), "r")
        self.map = map.read().split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)-1
        self.setStageList()

    def render(self):
        image = pygame.Surface(
            (self.width * MAP_TILE_WIDTH, self.height * MAP_TILE_HEIGHT)
        )
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                red, green, blue = 0, 0, 0
                color = ""
                if c in self.key.keys():
                    color = self.key[c]["color"]
                else:
                    color = self.key["_"]["color"]
                red, green, blue = [int(v) for v in color.split(",")]
                rect = pygame.Surface((MAP_TILE_WIDTH, MAP_TILE_HEIGHT))
                rect.fill((red, green, blue))
                image.blit(rect, (map_x * MAP_TILE_WIDTH, map_y * MAP_TILE_HEIGHT))
        return image

    def setStageList(self):
        for line in range(self.height):
            lineObjs = set(self.map[line])
            for letter in lineObjs:
                if letter not in self.key.keys():
                    col = self.map[line].find(letter)
                    self.stages.append([col, line, letter])

        self.stages.sort(key=lambda x: x[2])

    def nextExploration(self, chars):
        if self.running:
            return
        self.running = True

        if self.currStage == 0 or self.currStage == len(self.stages)-1:
            self.open_lst = []
        
        start_time = threading.Timer(0, self.explore, [chars])
        start_time.start()
    
    def endExploration(self):
        self.open_lst = []

    def explore(self, chars):
        if self.currStage == len(self.stages)-1:
            return
        start = self.stages[self.currStage]
        stop = self.stages[self.currStage + 1]
        start_time = threading.Timer(0.05, self.goTo, [start, stop])
        start_time.start()
        start_time.join()

        chars.solucionarEtapa(self.currStage)
        self.currStage += 1
        self.running = False

    def getTimeTravel(self, path):
        totalTime = 0
        for i in path:
            key = self.map[i[1]][i[0]]
            if key in self.key.keys():
                totalTime += int(self.key[key]["time"])
        return totalTime

    def goTo(self, start, stop):
        path = self.a_star_algorithm(start[:2], stop[:2])
        stop.append(self.getTimeTravel(path))
        print("Duration: {}".format(stop[-1]))

    def get_neighbors(self, v):
        neighbors = []
        if v[0] - 1 >= 0:
            neighbors.append([v[0] - 1, v[1]])
        if v[1] - 1 >= 0:
            neighbors.append([v[0], v[1] - 1])
        if v[1] + 1 < self.height:
            neighbors.append([v[0], v[1] + 1])
        if v[0] + 1 < self.width - 1:
            neighbors.append([v[0] + 1, v[1]])
        return neighbors

    def h(self, p, q):
        return math.dist(p, q)
        # abs(p[0] - q[0]) + abs(p[1] - q[1])
        # math.dist(p, q)

    def w(self, p):
        key = self.map[p[1]][p[0]]
        if key in self.key.keys():
            return int(self.key[key]["time"])
        return 0

    def a_star_algorithm(self, start, stop):
        print("Search A*: {} to {}".format(start, stop))
        # open_q - priority queue, stores candidate nodes for exploration
        # open_list - list, same as q but non-destructive, used for drawing
        # nodes_from - dict, keeps track of the ancestor of explored nodes
        # costs - dict, stores the cost of reaching explored nodes
        # NOTE: in this implementation, an explicit closed list is not used
        # instead, we can reuse the costs dict for this purpose

        self.open_q = PriorityQueue()
        self.open_q.put((0, start))
        self.open_lst = [start]  # used for drawing purposes only
        nodes_from = {}
        costs = {}
        nodes_from[str(start)] = None
        costs[str(start)] = 0

        while not self.open_q.empty():
            # time.sleep(0.0001)
            current_node = self.open_q.get()[1]
            if current_node == stop:
                reconst_path = []
                while current_node != start:
                    reconst_path.append(current_node)
                    current_node = nodes_from[str(current_node)]

                reconst_path.append(start)
                reconst_path.reverse()
                # print("Path found: {}".format(reconst_path))
                self.reconst_path += reconst_path
                return reconst_path

            for neighbor in self.get_neighbors(current_node):
                # print("NEIGHBOR:", neighbor)
                neighbor_cost = costs[str(current_node)] + self.w(neighbor)
                if str(neighbor) not in costs or neighbor_cost < costs[str(neighbor)]:
                    costs[str(neighbor)] = neighbor_cost
                    f = neighbor_cost + self.h(neighbor, stop)
                    self.open_q.put((f, neighbor))
                    self.open_lst.append(neighbor)
                    nodes_from[str(neighbor)] = current_node

        # path not found
        print("Path not found!")
        return None

    def getTotalTime(self):
        total = 0
        for i in self.stages:
            if len(i) > 3:
                total += i[3]
        return total

    def renderExploration(self):
        def getTiles(tileList, color, alpha):
            tiles = []
            tile = pygame.Surface((MAP_TILE_WIDTH, MAP_TILE_HEIGHT))
            tile.fill(color)
            tile.set_alpha(alpha)

            if hasattr(tileList, "queue"):
                tileList = tileList.queue

            for n in tileList:
                # print("Type n:", type(n))
                if type(n) is tuple:
                    n = n[1]
                tiles.append(
                    (
                        tile,
                        tile.get_rect(
                            topleft=(
                                n[0] * MAP_TILE_WIDTH + BORDER_X,
                                n[1] * MAP_TILE_HEIGHT + BORDER_Y,
                            )
                        ),
                    )
                )
            return tiles

        plots = []

        plots += getTiles(self.open_lst, (255, 50, 255), 170)
        plots += getTiles(self.reconst_path, (255, 90, 0), 170)

        return plots
    
    def renderInfo(self, chars):
        plots = []
        area = pygame.Surface((self.width * MAP_TILE_WIDTH, self.height * MAP_TILE_HEIGHT))
        area.fill((0,0,0))
        area.set_alpha(180)
        plots.append(( area, area.get_rect(topleft = (BORDER_X, BORDER_Y)) ))
        plots.append((FONT.render("Tempo de Deslocamento e de Realizacao", False, (255, 255, 255)),
                (BORDER_X + 20, BORDER_Y + 20)))
        realizacao = 0
        for i, s in enumerate(self.stages):
            if len(s) > 3:
                text = FONT.render("Etapa {}: {}, {:.3f}".format(i, s[-1], chars.tempoEtapa(i)), False, (255, 255, 255))
                realizacao += chars.tempoEtapa(i)
            else:
                text = FONT.render("Etapa {}".format(i), False, (255, 255, 255))
            plots.append((text,
                    (BORDER_X + 20 if i < len(self.stages) / 2 else BORDER_X * 5, 
                        BORDER_Y + 100 + 28 * (i % (len(self.stages) / 2)))))
        plots.append((FONT.render("Total: {}, {}".format(self.getTotalTime(), realizacao), False, (255, 255, 255)),
                (BORDER_X + 20, BORDER_Y + 60)))
        return plots



if __name__ == "__main__":    
    pygame.init()

    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900

    MAP_TILE_WIDTH = 3
    MAP_TILE_HEIGHT = 7

    BORDER_X = 110
    BORDER_Y = 223

    FONT = pygame.font.Font("assets/font.ttf", 17)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    blackBackground = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    blackBackground.fill((232, 208, 176))

    laterais = pygame.image.load('assets/laterais.png')
    laterais = pygame.transform.scale(laterais, (SCREEN_WIDTH, SCREEN_HEIGHT))

    moldura = pygame.image.load('assets/moldura.png')
    moldura = pygame.transform.scale(moldura, (moldura.get_size()[0] * 3.65, moldura.get_size()[1] * 3.6))
    
    title = pygame.image.load('assets/titulo.png')
    title = pygame.transform.scale(title, (title.get_size()[0] * 3.2, title.get_size()[1] * 3.2))

    level = Level()
    level.load_file("configs/level.map")

    clock = pygame.time.Clock()

    background = level.render()
    overlays = pygame.sprite.RenderUpdates()

    c = Characters()
    c.load_file("configs/chars.map")
    chars = c.render()

    exploring = False
    game_over = False
    info = False

    while not game_over:
        screen.blit(blackBackground, (0, 0))
        screen.blit(background, (BORDER_X, BORDER_Y))
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_SPACE:
                level.nextExploration(c)
                exploring = True
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_over = True
            if event.type == KEYDOWN and event.key == K_i:
                info = not info

        if exploring:
            screen.blits(level.renderExploration())
            chars = c.render()
            
        if info:
            screen.blits(level.renderInfo(c))

        screen.blit(title, (330, 30))

        screen.blit(moldura, (68, 193))

        screen.blit(laterais, (0, 0))

        screen.blit(chars, (1120.5, 57))

        overlays.draw(screen)
        pygame.display.flip()
        clock.tick(60)
