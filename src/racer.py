import config as cf
import vars as vr
import tools as t
import visuals as vs
import utils as u
from vector import *
from sprite import Sprite

import pygame as pg

class Racer(Sprite):
    def __init__(self, world_position, size, angle=0, offset_position=(0, 0)):
        super().__init__(world_position, size)

        self.ingame_position = Vector(*offset_position)
        vr.world.game_center = world_position if isinstance(world_position, Vector) else Vector(*world_position)
        self.angle = rad(angle)
        self.speed, self.angle_speed = 0, 0

        self.visuals = vs.racer_visuals
        self.visual_current = self.visuals['straight']

        self.detector = [vr.world.game_center + Vector(-self.size.width()*0.4, -self.size.length()*0.3),
                         vr.world.game_center + Vector(self.size.width()*0.4, -self.size.length()*0.3),
                         vr.world.game_center + Vector(-self.size.width()*0.4, self.size.length()*0.3),
                         vr.world.game_center + Vector(self.size.width()*0.4, self.size.length()*0.3)]
        self.wall_detection = [False for _ in range(len(self.detector))]

    def update(self):

        max_speed = 1000
        grass_speed = 500
        backward_speed = 150
        if vr.inputs['UP']:
            self.speed = min(max_speed, self.speed + 15)
        if vr.inputs['DOWN']:
            self.speed = 0.95 * self.speed

        if vr.race.track.touch(vr.world.world_position(vr.world.ingame_middle() + self.ingame_position)):
            self.speed = self.speed * 0.99
        else:
            if self.speed > grass_speed: self.speed = self.speed * 0.9
            else: self.speed = self.speed * 0.99

        if vr.inputs['RIGHT']:
            self.angle_speed = (0 if self.speed < 100 else 2 * min(40, 8 * t.inv(self.speed**0.3)))
        elif vr.inputs['LEFT']:
            self.angle_speed = -1 * (0 if self.speed < 100 else 2 * min(40, 8 * t.inv(self.speed**0.3)))
        else:
            self.angle_speed = 0.9 * self.angle_speed

        slide_direction = Vector(define_by_angle=True, angle=self.angle + rad(90), norm=1)
        sliding_vector = slide_direction * (0 if self.speed < 100 else -1 * t.s(self.angle_speed) * min(200, 10000 * (self.angle_speed ** 2) * t.inv(self.speed)))

        if self.wall_detection[2]:
            self.angle_speed = min(0.5, self.angle_speed)
        elif self.wall_detection[3]:
            self.angle_speed = max(-0.5, self.angle_speed)

        self.angle = (self.angle + self.angle_speed * cf.dt) % 6.29

        if self.wall_detection[0]:
            self.angle += 10 * cf.dt
        elif self.wall_detection[1]:
            self.angle += -10 * cf.dt

        vr.world.update(Vector(define_by_angle=True, angle=self.angle, norm=1) * self.speed + sliding_vector)
        self.world_position = vr.world.game_center

        self.detector = [vr.world.game_center + u.RotateVector(Vector(-self.size.width() * 0.4, -self.size.length() * 0.4), self.angle + 1.57),
                         vr.world.game_center + u.RotateVector(Vector(self.size.width() * 0.4, -self.size.length() * 0.4), self.angle + 1.57),
                         vr.world.game_center + u.RotateVector(Vector(-self.size.width() * 0.4, self.size.length() * 0.4), self.angle + 1.57),
                         vr.world.game_center + u.RotateVector(Vector(self.size.width() * 0.4, self.size.length() * 0.4), self.angle + 1.57)]

        self.update_visual()
        self.draw()

    def update_visual(self):
        if abs(self.angle_speed) >= 1:
            if abs(self.angle_speed) >= 5:
                self.visual_current = self.visuals['turn_high']
            self.visual_current = self.visuals['turn_low']
        else:
            self.visual_current = self.visuals['straight']
        if self.angle_speed < 0:
            self.visual_current.setflip(False, True)
        else:
            self.visual_current.setflip(False, False)

    def draw(self):
        vr.game_window.blit(*u.Rotate(self.visual_current.get_frame(), degrees(self.angle), center=(vr.world.ingame_middle() + self.ingame_position)(), pivot_from_topleft=(self.size.size / 2)()))

        print_detector = False
        if print_detector:
            for d_index, detected in enumerate(self.wall_detection):
                pg.draw.circle(vr.game_window, 'green' if detected else 'red',vr.world.ingame_position(self.detector[d_index])(), 5)
        #pg.draw.line(vr.game_window, 'blue', self.position(), (self.position + Vector(define_by_angle=True, angle=self.angle, norm=50))(), width=5)


class BotRacer(Sprite):
    def __init__(self, world_position, size, angle=0):
        super().__init__(world_position, size)

        self.angle = rad(angle)
        self.speed, self.angle_speed = 0, 0

        self.visuals = vs.bot_visuals
        self.visual_current = self.visuals['straight']

        self.road_position = 0
        self.target_randomness = NullVector()

    def update(self):

        next_tile = vr.race.track.next_tile(self.road_position)
        if t.distance(self.world_position(), (next_tile.world_position + self.target_randomness)()) < next_tile.area.size.width()/2:
            self.road_position += 1
            next_tile = vr.race.track.next_tile(self.road_position)
            width = next_tile.area.size.width()
            self.target_randomness = Vector(max(-width/2, min(width/2, self.target_randomness.x + t.rndInt(-width/8, width/8))) , 0)
        else:
            pass

        target = (next_tile.world_position - self.world_position) + self.target_randomness
        direction = target.normalised()

        #pg.draw.line(vr.game_window, 'white', vr.world.ingame_position(self.world_position())(), vr.world.ingame_position(self.world_position + target)(), 5)

        max_speed = 1200
        angle_slow = 1.57 * 0.9 # pi/2 * factor
        turn_power = 0.1

        self.speed = min(max_speed * max(0.1, (angle_slow - abs(u.angle_diff(self.angle, direction.angle)))/angle_slow), self.speed + t.rndInt(3, 17))
        self.turn_angle(direction.angle, turn_power)

        slide_direction = Vector(define_by_angle=True, angle=self.angle + rad(90), norm=1)
        sliding_vector = slide_direction * (0 if self.speed < 100 else -1 * t.s(self.angle_speed) * min(200, 10000 * (self.angle_speed ** 2) * t.inv(self.speed)))

        self.world_position = self.world_position + Vector(define_by_angle=True, angle=self.angle, norm=1) * self.speed * cf.dt + sliding_vector

        self.update_visual()
        self.draw()

    def turn_angle(self, angle_target, turn_factor):
        diff = (angle_target - self.angle + 3.14) % (2 * 3.14) - 3.14
        self.angle = (self.angle + diff * turn_factor) % (2 * 3.14)

    def update_visual(self):
        if abs(self.angle_speed) >= 1:
            if abs(self.angle_speed) >= 5:
                self.visual_current = self.visuals['turn_high']
            self.visual_current = self.visuals['turn_low']
        else:
            self.visual_current = self.visuals['straight']
        if self.angle_speed < 0:
            self.visual_current.setflip(False, True)
        else:
            self.visual_current.setflip(False, False)

    def draw(self):
        vr.game_window.blit(*u.Rotate(self.visual_current.get_frame(), degrees(self.angle), center=vr.world.ingame_position(self.world_position), pivot_from_topleft=(self.size.size / 2)()))
        #pg.draw.line(vr.game_window, 'blue', self.position(), (self.position + Vector(define_by_angle=True, angle=self.angle, norm=50))(), width=5)

