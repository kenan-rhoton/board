import os, sys, math, time, random
import pygame
from pygame.locals import *

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

pygame.init()
random.seed()

GAME_SCALE = 45
DEFAULT_FONT = pygame.font.get_default_font()
TEXT_FONT = pygame.font.SysFont(DEFAULT_FONT, (GAME_SCALE*3)//4)
TEXT_FONT_SMALL = pygame.font.SysFont(DEFAULT_FONT, (GAME_SCALE)//2)
BACKGROUND = None
if len(sys.argv) >= 2:
    BACKGROUND=sys.argv[1]

def dist(origin, dest):
    return math.hypot(dest[0] - origin[0], dest[1] - origin[1])

def average(origin, dest):
    return ((dest[0] + origin[0])//2, (dest[1] + origin[1])//2)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clear()
        if BACKGROUND is None:
            self.background = pygame.Surface(self.screen.get_size())
            self.background = self.background.convert()
            self.background.fill((250, 250, 250))
        else:
            self.background = pygame.image.load(BACKGROUND)
            self.background.convert()
            self.background = pygame.transform.scale(self.background, self.screen.get_size())

    def clear(self):
        self.dudes = []
        self.terrain = []
        self.selection = None
        self.line = None
        self.edit = False
        self.drag = False
        self.roll = []
        self.multiplier = 1
        self.click = time.time()

    def start(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and self.edit:
                    if event.key == K_RETURN or event.key == K_ESCAPE:
                        self.edit = False
                        self.selection = None
                    else:
                        self.selection.send_key(event.key)
                elif event.type == KEYDOWN and event.key == K_c and event.mod & KMOD_CTRL:
                    self.clear()
                elif event.type == KEYDOWN and event.key == K_r:
                    self.create_dude((255,0,0))
                elif event.type == KEYDOWN and event.key == K_g:
                    self.create_dude((0,255,0))
                elif event.type == KEYDOWN and event.key == K_b:
                    self.create_dude((0,0,255))
                elif event.type == KEYDOWN and (event.key == K_DELETE or event.key == K_BACKSPACE):
                    self.delete_selection()
                elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_d):
                    self.roll = [random.randint(1,6) for _ in range(self.multiplier)]
                elif event.type == KEYDOWN and K_0 <= event.key <= K_9:
                    self.multiplier = int(pygame.key.name(event.key))
                elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                    if self.line is None:
                        self.line = pygame.mouse.get_pos()
                elif event.type == MOUSEBUTTONUP and event.button == 3:
                    self.line = None
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.select(pygame.mouse.get_pos())
                    self.drag = True
                    if self.double_click():
                        self.edit = True
                    else:
                        self.edit = False
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    self.drag = False
                elif event.type == MOUSEMOTION and self.selection is not None:
                    if self.drag:
                        self.selection.move(pygame.mouse.get_pos())
            self.draw()

    def delete_selection(self):
        if self.selection is not None:
            self.dudes.remove(self.selection)
            self.selection = None

    def double_click(self):
        now = time.time()
        if now - self.click < 0.5:
            return True
        self.click = now
        return False

    def create_dude(self, color):
        self.dudes.append(Dude(color))

    def select(self, pos):
        for dude in reversed(self.dudes):
            if dude.within(pos):
                self.selection = dude
                return
        self.selection = None

    def draw_ruler(self):
        if self.line is not None:
            pos = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, (80,190,0), self.line, pos, 5)
            fmt = "{distance:.1f}\""
            txt = TEXT_FONT.render(fmt.format(distance=dist(self.line, pos)/GAME_SCALE), True, (0,0,0))
            avg = average(self.line, pos)
            dest = (avg[0] - txt.get_width()//2, avg[1] - GAME_SCALE//4 - txt.get_height()//2)
            self.screen.blit(txt, dest)

    def draw_roll(self):
        roll = ",".join(map(str, self.roll))
        txt = TEXT_FONT.render(roll, True, (0,0,0))
        pos = (self.screen.get_width() - GAME_SCALE - txt.get_width(), GAME_SCALE)
        self.screen.blit(txt, pos)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for dude in self.dudes:
            dude.draw(self.screen)
        self.draw_ruler()
        self.draw_roll()
        pygame.display.flip()

class Dude:
    def __init__(self, color):
        self.pos = (GAME_SCALE//2,GAME_SCALE//2)
        self.color = color
        self.name = ""

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, GAME_SCALE//2)
        txt = TEXT_FONT_SMALL.render(self.name.upper(), True, (0,0,0))
        text_pos = (self.pos[0] - txt.get_width()//2, self.pos[1] - txt.get_height()//2)
        screen.blit(txt, text_pos)

    def within(self, pos):
        if pos[0] > self.pos[0] - GAME_SCALE//2 and pos[0] < self.pos[0] + GAME_SCALE//2:
            if pos[1] > self.pos[1] - GAME_SCALE//2 and pos[1] < self.pos[1] + GAME_SCALE//2:
                return True
        return False

    def send_key(self, key):
        if key == K_DELETE:
            self.name = ""
        elif K_a <= key <= K_z or K_0 <= key <= K_9:
            self.name += pygame.key.name(key)

    def move(self, pos):
        self.pos = pos

screen = pygame.display.set_mode((GAME_SCALE*30, GAME_SCALE*22))
pygame.display.set_caption('Board')
game = Game(screen)
game.start()
