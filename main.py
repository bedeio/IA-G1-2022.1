import pygame
import pygame.locals
from pygame.locals import *
import configparser
import threading
import time
import math


class Level(object):
    def __init__(self):
        self.stages = []
        self.map = []
        self.key = {}
        self.width = 0
        self.height = 0

        # a* state
        self.open_lst = set([])
        self.closed_lst = set([])
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
        self.height = len(self.map)
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
                rect = pygame.Surface((MAP_TILE_WIDTH - 1, MAP_TILE_HEIGHT - 1))
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

    def initExploration(self):
        start_time = threading.Timer(0, self.explore)
        start_time.start()

    def explore(self):
        for i in range(len(self.stages) - 1):
            start = self.stages[i]
            stop = self.stages[i + 1]
            start_time = threading.Timer(0.5, self.goTo, [start, stop])
            start_time.start()
            start_time.join()

            if game_over:
                break

        self.open_lst = set([])
        self.closed_lst = set([])

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
        if v[1] + 1 < self.height - 1:
            neighbors.append([v[0], v[1] + 1])
        if v[0] + 1 < self.width - 1:
            neighbors.append([v[0] + 1, v[1]])
        return neighbors

    def h(self, p, q):
        return math.dist(p, q)

    def w(self, p):
        key = self.map[p[1]][p[0]]
        if key in self.key.keys():
            return int(self.key[key]["time"])
        return 0

    def a_star_algorithm(self, start, stop):
        print("Search A*: {} to {}".format(start, stop))
        # In this open_lst is a lisy of nodes which have been visited, but who's
        # neighbours haven't all been always inspected, It starts off with the start
        # node
        # And closed_lst is a list of nodes which have been visited
        # and who's neighbors have been always inspected
        self.open_lst = [start]
        self.closed_lst = []

        # poo has present distances from start to all other nodes
        # the default value is +infinity
        poo = {}
        poo[str(start)] = 0

        # par contains an adjac mapping of all nodes
        par = {}
        par[str(start)] = start

        while len(self.open_lst) > 0:
            # time.sleep(0.0001)
            n = None

            # it will find a node with the lowest value of f() -
            for v in self.open_lst:
                if n == None or poo[str(v)] + self.h(v, stop) < poo[str(n)] + self.h(
                    n, stop
                ):
                    n = v

            if n == None:
                print("Path does not exist!")
                return None

            # if the current node is the stop
            # then we start again from start
            if n == stop:
                reconst_path = []

                while par[str(n)] != n:
                    reconst_path.append(n)
                    n = par[str(n)]

                reconst_path.append(start)

                reconst_path.reverse()

                print("Path found: {}".format(reconst_path))
                self.reconst_path += reconst_path
                return reconst_path

            # for all the neighbors of the current node do
            for neighbor in self.get_neighbors(n):
                # if the current node is not presentin both open_lst and closed_lst
                # add it to open_lst and note n as it's par
                if neighbor not in self.open_lst and neighbor not in self.closed_lst:
                    self.open_lst.append(neighbor)
                    par[str(neighbor)] = n
                    poo[str(neighbor)] = poo[str(n)] + self.w(neighbor)

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update par data and poo data
                # and if the node was in the closed_lst, move it to open_lst
                else:
                    if poo[str(neighbor)] > poo[str(n)] + self.w(neighbor):
                        poo[str(neighbor)] = poo[str(n)] + self.w(neighbor)
                        par[str(neighbor)] = n

                        if neighbor in self.closed_lst:
                            self.closed_lst.remove(neighbor)
                            self.open_lst.append(neighbor)

            # remove n from the open_lst, and add it to closed_lst
            # because all of his neighbors were inspected
            self.open_lst.remove(n)
            self.closed_lst.append(n)

        print("Path does not exist!")
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
            for n in tileList:
                plots.append(
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
        plots += getTiles(self.closed_lst, (255, 125, 255), 170)
        plots += getTiles(self.reconst_path, (255, 90, 0), 170)

        font = pygame.font.SysFont("monospace", 24, True)

        plots.append(
            (
                font.render(
                    "Total: {}".format(self.getTotalTime()), False, (255, 255, 255)
                ),
                (self.width * MAP_TILE_WIDTH + BORDER_X + 20, 50),
            )
        )
        for i, s in enumerate(self.stages):
            if len(s) > 3:
                plots.append(
                    (
                        font.render(
                            "Etapa {}: {}".format(i, s[-1]), False, (255, 255, 255)
                        ),
                        (
                            self.width * MAP_TILE_WIDTH + BORDER_X + 20,
                            23 * (i + 1) + 50,
                        ),
                    )
                )
            else:
                plots.append(
                    (
                        font.render("Etapa {}".format(i), False, (255, 255, 255)),
                        (
                            self.width * MAP_TILE_WIDTH + BORDER_X + 20,
                            23 * (i + 1) + 50,
                        ),
                    )
                )

        return plots


if __name__ == "__main__":
    pygame.init()

    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800

    MAP_TILE_WIDTH = 2
    MAP_TILE_HEIGHT = 5

    BORDER_X = 20
    BORDER_Y = 60

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    blackBackground = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    blackBackground.fill((0, 0, 0))

    level = Level()
    level.load_file("map/level.map")

    clock = pygame.time.Clock()

    background = level.render()
    overlays = pygame.sprite.RenderUpdates()

    exploring = False
    game_over = False

    while not game_over:
        screen.blit(blackBackground, (0, 0))
        screen.blit(background, (BORDER_X, BORDER_Y))
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_SPACE:
                level.initExploration()
                exploring = True
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_over = True

        if exploring:
            screen.blits(level.renderExploration())

        overlays.draw(screen)
        pygame.display.flip()
        clock.tick(30)
