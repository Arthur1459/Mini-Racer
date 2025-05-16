import config as cf
import vars as vr
import tools as t
import visuals as vs
import utils as u
from vector import *

import pygame as pg

class Sprite:
    def __init__(self, position=(0, 0), size=cf.racer_size):
        self.id = u.getNewId()
        self.tags = {'sprite'}

        self.world_position = position if isinstance(position, Vector) else Vector(*position)
        self.size = Size(*size)

    def topleft(self):
        return (self.world_position - self.size.size / 2)()

    def update(self):
        pass

    def draw(self):
        pg.draw.rect(vr.game_window, 'red', [*self.world_position(), *self.size()], width=4)
