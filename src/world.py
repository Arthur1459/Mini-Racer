import config as cf
import tools as t
from vector import *
import vars as vr

class World:
    def __init__(self, size: Size, game_center: Vector):

        self.world_size = size
        self.game_center = game_center
        self.game_size = Size(*cf.game_resolution)

    def world_position(self, ingame_position: Vector) -> Vector:
        return ingame_position + self.game_center - self.ingame_middle()
    def ingame_position(self, world_position) -> Vector:
        return world_position - self.game_center + self.ingame_middle()
    def ingame_middle(self) -> Vector: return self.game_size.size / 2
    def hud_position(self, world_position: Vector) -> Vector:
        return (world_position - self.game_center + self.game_size.size/2) / cf.scale

    def update(self, racer_speed: Vector):

        self.game_center = self.game_center + racer_speed * cf.dt

        if vr.inputs['CLICK']:
            self.game_center = vr.cursor_world

        self.game_center.x = t.bound(self.game_center.x, 0, self.world_size.x)
        self.game_center.y = t.bound(self.game_center.y, 0, self.world_size.y)

        return
