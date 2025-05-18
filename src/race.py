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

        self.track = Road(Vector(*cf.world_size) / 2, width=350)
        self.start_angle = 0
        self.terrain = []

        self.load_circuit()

        self.nb_bots = nb_bots
        self.player = None
        self.bots = None
        self.racers = None
        self.racers_info = None
        self.reset()

        self.ranking = {}

        self.rank_box = pg.Surface((300, 50), pg.SRCALPHA)
        self.rank_box.fill((100, 100, 100, 128))

    def update(self):
        self.track.update()

        for terrain in self.terrain:
            terrain.update()
            self.player.wall_detection = terrain.touch(self.player.detector)

        if self.started:
            if vr.inputs['R']:
                self.started = False
                self.reset()
                return

            for bot in self.bots:
                bot.update()

            self.player.update()

            self.update_ranking()
            self.display_ranking()

        else:
            vr.world.update(NullVector())

            for bot in self.bots:
                bot.draw()

            self.player.draw()

            if vr.inputs['SPACE']:
                self.started = True

        # pg.draw.circle(vr.game_window, 'green' if collide_test else 'blue', vr.middle, 10)

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

    def display_ranking(self):
        u.Text(f"{self.ranking[self.player]} /{len(self.racers)}", (vr.gwin_width//2 - 90, 40), 48, 'white')
        u.Text(f"LAP {self.racers_info[self.player]['lap']} /?", (40, 20), 48, 'white')
        u.Text(f"CHECK {'detected' if self.racers_info[self.player]['checkpoint'] else 'undetected'}", (40, 60), 32, 'green' if self.racers_info[self.player]['checkpoint'] else 'red')
        u.Text(f"CURRENT {(vr.t - self.racers_info[self.player]['time']):.2f} s", (vr.gwin_width - 300, 10), 24, 'green' if self.racers_info[self.player]['best_time'] is None or (vr.t - self.racers_info[self.player]['time']) < self.racers_info[self.player]['best_time'] else 'red')
        if self.racers_info[self.player]['best_time'] is not None: u.Text(f"BEST {self.racers_info[self.player]['best_time']:.2f} s", (vr.gwin_width - 300, 40), 24, 'white')
        if self.racers_info[self.player]['last_time'] is not None: u.Text(f"LAST {self.racers_info[self.player]['last_time']:.2f} s", (vr.gwin_width - 300, 70), 16, 'white')

        for racer in self.racers:
            vr.game_window.blit(self.rank_box, (50, 200 + 60 * self.ranking[racer]))
            u.Text(f"{self.ranking[racer]}: {racer.name}", (50 + 10, 200 + 60 * self.ranking[racer] - 1) , 40, 'white' if racer != self.player else 'red')
            if self.ranking[racer] == 1:
                vr.game_window.blit(vs.crown, (vr.world.ingame_position(racer.world_position) + Vector(0, -1.5 * cf.racer_size[1]))())

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

    race.terrain.append(Block(Vector(*cf.world_size) / 2 + Vector(900, 500),
                              [Vector(-550, -950), Vector(-450, -800), Vector(-280, -400),
                               Vector(90, -150), Vector(660, -140), Vector(1000, -180),
                               Vector(1020, -100), Vector(640, 200), Vector(480, 420),
                               Vector(480, 750), Vector(110, 620), Vector(-360, 560),
                               Vector(-1020, 600), Vector(-1180, 520), Vector(-890, 410),
                               Vector(-660, 170), Vector(-560, -180), Vector(-650, -700), ]))