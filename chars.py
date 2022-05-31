import configparser


class Char(object):
    def __init__(self, name, speed, lifes, image):
        self.name = name
        self.lifes = lifes
        self.speed = speed
        self.image = image


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

c = Characters()
c.load_file("configs/chars.map")