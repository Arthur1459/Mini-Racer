import time

import config as cf
import tools as t
import utils as u
from vector import *
from terrain import *
from racer import Racer, BotRacer
import vars as vr
import visuals as vs

import pygame as pg
from math import cos, sin

class Race:
    def __init__(self, nb_bots=10):
        self.started = False
        self.start_count, self.starting = 0, False

        self.track = Road(Vector(*cf.world_size) / 2, width=350)
        self.start_angle = 0
        self.terrain = {'wall': [], 'moving': []}

        self.load_circuit()

        self.nb_bots = nb_bots
        self.player = None
        self.bots = None
        self.racers = None
        self.racers_info = None
        self.reset()

        self.ranking = {}

        self.text_box = pg.Surface((150, 20), pg.SRCALPHA)
        self.text_box.fill((100, 100, 100, 128))

    def update(self):
        self.track.update()

        # Update Terrain (~hitbox) and player collision detection
        for terrain in (self.terrain['wall'] + self.terrain['moving']):
            if t.distance(terrain.world_position, self.player.world_position) > vr.world.game_size.radius(): continue
            terrain.update()
            for bot in self.bots:
                if terrain.owner != bot:
                    detection = terrain.touch(bot.detector)
                    bot.wall_detection = [bot.wall_detection[i] or detection[i] for i in range(len(bot.wall_detection))]

            if terrain.owner != self.player:
                detection = terrain.touch(self.player.detector)
                for i in range(len(self.player.wall_detection)):
                    self.player.wall_detection[i] = self.player.wall_detection[i] or detection[i]
                    self.player.wall_detection_owner[i] = terrain.owner

        # Reset moving hitbox with the player_one
        self.terrain['moving'] = [InvisibleBlock(self.player.world_position,
                                [u.RotateVector(Vector(-self.player.size.width() * 0.5, -self.player.size.length() * 0.5), self.player.angle + 1.57),
                                             u.RotateVector(Vector(self.player.size.width() * 0.5, -self.player.size.length() * 0.5), self.player.angle + 1.57),
                                             u.RotateVector(Vector(self.player.size.width() * 0.5, self.player.size.length() * 0.45), self.player.angle + 1.57),
                                             u.RotateVector(Vector(-self.player.size.width() * 0.5, self.player.size.length() * 0.45), self.player.angle + 1.57)],
                                             show=False, owner=self.player)]

        if self.started:
            if vr.inputs['R']:
                self.started = False
                self.reset()
                return

            for bot in self.bots:
                bot.update(draw=(t.distance(bot.world_position, self.player.world_position) < vr.world.game_size.radius()))
                bot.wall_detection = [False for _ in range(len(bot.wall_detection))]
                self.terrain['moving'].append(InvisibleBlock(bot.world_position,
                                [u.RotateVector(Vector(-bot.size.width() * 0.5, -bot.size.length() * 0.5), bot.angle + 1.57),
                                             u.RotateVector(Vector(bot.size.width() * 0.5, -bot.size.length() * 0.5), bot.angle + 1.57),
                                             u.RotateVector(Vector(bot.size.width() * 0.5, bot.size.length() * 0.45), bot.angle + 1.57),
                                             u.RotateVector(Vector(-bot.size.width() * 0.5, bot.size.length() * 0.45), bot.angle + 1.57)], show=False, owner=bot))

            self.player.update()
            self.player.wall_detection = [False for _ in range(len(self.player.wall_detection))]
            self.player.wall_detection_owner = [None for _ in range(len(self.player.wall_detection))]

            self.update_ranking()
            self.display_hud()

        else:
            vr.world.update(NullVector())

            for bot in self.bots:
                bot.draw()

            self.player.draw()

            if vr.inputs['SPACE']:
                self.starting = True
                self.start_count = vr.t
            elif self.starting and (vr.t - self.start_count) < 3:
                u.Text(f"{3 - int(vr.t - self.start_count)}", (Vector(*vr.win_middle) - Vector(14, 28))(), 72, 'yellow')
            elif self.starting:
                self.starting = False
                self.started = True

        #pg.draw.circle(vr.game_window, 'green' if collide_test else 'blue', vr.middle, 10)

    def update_ranking(self):
        ranking_data = []
        for racer in self.racers:
            self.racers_info[racer]['track_position'] = self.track.get_position(racer.world_position, self.racers_info[racer]['track_position'])

            if racer != self.player:
                if self.racers_info[racer]['checkpoint'] and self.racers_info[racer]['track_position'] == 0:
                    self.racers_info[racer]['lap'] += 1
                    self.racers_info[racer]['checkpoint'] = False
                elif self.racers_info[racer]['track_position'] == len(self.track.tiles) // 2:
                    self.racers_info[racer]['checkpoint'] = True
            else:
                if self.racers_info[self.player]['checkpoint'] and self.racers_info[self.player]['track_position'] == 0:
                    self.racers_info[self.player]['last_time'] = (vr.t - self.racers_info[self.player]['time']) if \
                    self.racers_info[self.player]['lap'] > 0 else None
                    if self.racers_info[self.player]['best_time'] is None or self.racers_info[self.player][
                        'last_time'] < \
                            self.racers_info[self.player]['best_time']:
                        self.racers_info[self.player]['best_time'] = self.racers_info[self.player]['last_time']
                    self.racers_info[self.player]['lap'] += 1
                    self.racers_info[self.player]['checkpoint'] = False
                    self.racers_info[self.player]['time'] = vr.t
                elif self.racers_info[self.player]['track_position'] == len(self.track.tiles) // 2:
                    self.racers_info[self.player]['checkpoint'] = True

            ranking_data.append((self.track.nb_tiles * self.racers_info[racer]['lap'] + self.racers_info[racer]['track_position'] - t.distance(racer.world_position(), self.track.tiles[self.racers_info[racer]['track_position']].world_position())/(self.track.tiles[self.racers_info[racer]['track_position']].area.size.length()), racer))

        ranking_data.sort(key=lambda x: x[0], reverse=True)
        for rank, (_, racer) in enumerate(ranking_data, start=1):
            self.ranking[racer] = rank

    def display_hud(self):
        u.Text(f"{self.ranking[self.player]} /{len(self.racers)}", (vr.win_width//2 - 40, 20), 24, 'white')
        u.Text(f"LAP {self.racers_info[self.player]['lap']} /?", (20, 10), 24, 'white')
        u.Text(f"CHECK {'detected' if self.racers_info[self.player]['checkpoint'] else 'undetected'}", (20, 32), 12, 'green' if self.racers_info[self.player]['checkpoint'] else 'red')
        u.Text(f"CURRENT {(vr.t - self.racers_info[self.player]['time']):.2f} s", (vr.win_width - 140, 5), 12, 'green' if self.racers_info[self.player]['best_time'] is None or (vr.t - self.racers_info[self.player]['time']) < self.racers_info[self.player]['best_time'] else 'red')
        if self.racers_info[self.player]['best_time'] is not None: u.Text(f"BEST {self.racers_info[self.player]['best_time']:.2f} s", (vr.win_width - 140, 20), 12, 'white')
        if self.racers_info[self.player]['last_time'] is not None: u.Text(f"LAST {self.racers_info[self.player]['last_time']:.2f} s", (vr.win_width - 140, 35), 12, 'white')

        for racer in self.racers:
            vr.hud_window.blit(self.text_box, (20, 100 + 30 * self.ranking[racer]))
            u.Text(f"{self.ranking[racer]}: {racer.name}", (20 + 5, 102 + 30 * self.ranking[racer] - 1) , 16, 'white' if racer != self.player else 'red')
            if self.ranking[racer] == 1:
                vr.game_window.blit(vs.crown, vr.world.ingame_position(racer.world_position) - Vector(0, cf.racer_size[1]))

    def reset(self):
        direction = self.track.tiles[0].direction
        width = self.track.tiles[0].area.size.width()
        angle = self.track.tiles[0].area.angle
        self.bots = [
            BotRacer(Vector(*cf.world_size)/2 - ((i + 2) * 1.05 * cf.racer_size[1] * direction) + (1 if i % 2 == 0 else -1) * Vector(define_by_angle=True, angle=angle + rad(90), norm=width/4), cf.racer_size,
                     angle=self.start_angle, skills=(1.4 - (1.4 - 0.6) * (i + 0.5)/self.nb_bots)) for i in range(self.nb_bots)]
        self.player = Racer(Vector(*cf.world_size)/2 - ((self.nb_bots + 2) * 1.05 * cf.racer_size[1] * direction) + (1 if self.nb_bots % 2 == 0 else -1) * Vector(define_by_angle=True, angle=angle + rad(90), norm=width/4), cf.racer_size, angle=self.start_angle)
        self.racers = [self.player] + self.bots
        self.racers_info = {racer: {'lap': 0, 'checkpoint': True, 'time': vr.t, 'last_time': None, 'best_time': None,
                                    'track_position': 0} for racer in self.racers}

        self.ranking = {}
        self.started = False
        self.starting = False

    def load_circuit(self):
        suzuka(self)


def suzuka(race):
    race.start_angle = 45

    race.track.addStraight(3000, angle=race.start_angle)
    #race.track.addStraight(2500)
    race.track.addTurn(45, 5, 100)
    race.track.addStraight(250)
    race.track.addTurn(135, 5, 40)
    race.track.addStraight(500)
    race.track.addTurn(-60, 6, 100)
    race.track.addTurn(90, 6, 100)
    race.track.addTurn(-90, 6, 100)
    race.track.addTurn(110, 5, 100)
    race.track.addStraight(300)
    race.track.addTurn(-90, 5, 100)
    race.track.addTurn(-75, 3, 150)
    race.track.addStraight(200)
    race.track.addTurn(40, 8, 40)
    race.track.addStraight(500)
    race.track.addTurn(90, 8, 40)
    race.track.addStraight(2000)
    race.track.addTurn(40, 6, 40)
    race.track.addStraight(1200)
    race.track.addTurn(-170, 10, 100)
    race.track.addStraight(1000)
    race.track.addTurn(80, 5, 200)
    race.track.addStraight(1000)
    race.track.addTurn(45, 5, 100)
    race.track.addStraight(1000)
    race.track.addTurn(-75, 5, 75)
    race.track.addStraight(300)
    race.track.addTurn(-140, 5, 90)
    race.track.addStraight(1500)
    race.track.addTurn(-10, 5, 50)
    race.track.addStraight(4100)
    race.track.addTurn(-45, 5, 50)
    race.track.addStraight(500)
    race.track.addTurn(-14, 2, 50)
    race.track.addStraight(1200)
    race.track.addTurn(10, 5, 50)
    race.track.addStraight(150)
    race.track.addTurn(90, 5, 50)
    race.track.addStraight(100)
    race.track.addTurn(-90, 5, 50)
    race.track.addStraight(130)
    race.track.addTurn(84, 5, 150)
    race.track.addStraight(250)

def track_test(race):
    race.start_angle = -90

    race.track.addStraight(600, angle=-90)
    race.track.addTurn(45, 5, 100)
    race.track.addStraight(200)
    race.track.addTurn(135, 5, 40)
    race.track.addStraight(300)
    race.track.addTurn(-90, 5, 50)
    race.track.addStraight(600)
    race.track.addStraight(600)
    race.track.addTurn(135, 6, 75)
    race.track.addStraight(300)
    race.track.addTurn(-45, 5, 100)
    race.track.addTurn(135, 5, 75)
    race.track.addTurn(-45, 5, 100)
    race.track.addStraight(913)
    race.track.addTurn(90, 5, 50)
    race.track.addTurn(90, 5, 50)
    race.track.addTurn(-90, 5, 50)
    race.track.addStraight(100)

    race.terrain['wall'].append(Block(Vector(*cf.world_size) / 2 + Vector(900, 500),
                              [Vector(-550, -950), Vector(-450, -800), Vector(-280, -400),
                               Vector(90, -150), Vector(660, -140), Vector(1000, -180),
                               Vector(1020, -100), Vector(640, 200), Vector(480, 420),
                               Vector(480, 750), Vector(110, 620), Vector(-360, 560),
                               Vector(-1020, 600), Vector(-1180, 520), Vector(-890, 410),
                               Vector(-660, 170), Vector(-560, -180), Vector(-650, -700), ]))