import time

import config as cf
import tools as t
import utils as u
from vector import *
from terrain import *
from racer import Racer, BotRacer
import vars as vr

import pygame as pg
from math import cos, sin

class Race:
    def __init__(self, nb_bots=10):
        self.started = False

        self.track = Road(Vector(*cf.world_size) / 2, width=350)
        self.terrain = []

        self.load_circuit()

        self.nb_bots = nb_bots
        self.player = None
        self.bots = None
        self.racers = None
        self.racers_info = None
        self.reset()

        self.ranking = {}

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
        if self.racers_info[self.player]['last_time'] is not None: u.Text(f"LAST {self.racers_info[self.player]['last_time']:.2f} s", (vr.gwin_width - 300, 70), 18, 'white')

    def reset(self):
        self.player = Racer(Vector(*cf.world_size) / 2, cf.racer_size, angle=-90)
        self.bots = [
            BotRacer(Vector(*cf.world_size) / 2 + Vector(t.rndInt(-100, 100), t.rndInt(-100, 100)), cf.racer_size,
                     angle=-90) for _ in range(self.nb_bots)]
        self.racers = [self.player] + self.bots
        self.racers_info = {racer: {'lap': 0, 'checkpoint': True, 'time': vr.t, 'last_time': None, 'best_time': None,
                                    'track_position': 0} for racer in self.racers}

        self.ranking = {}

    def load_circuit(self):
        self.track.addStraight(600, angle=-90)
        self.track.addTurn(45, 5, 100)
        self.track.addStraight(200)
        self.track.addTurn(135, 5, 40)
        self.track.addStraight(300)
        self.track.addTurn(-90, 5, 50)
        self.track.addStraight(600)
        self.track.addStraight(600)
        self.track.addTurn(135, 6, 75)
        self.track.addStraight(300)
        self.track.addTurn(-45, 5, 100)
        self.track.addTurn(135, 5, 75)
        self.track.addTurn(-45, 5, 100)
        self.track.addStraight(913)
        self.track.addTurn(90, 5, 50)
        self.track.addTurn(90, 5, 50)
        self.track.addTurn(-90, 5, 50)
        self.track.addStraight(100)

        self.terrain.append(Block(Vector(*cf.world_size) / 2 + Vector(900, 500),
                                [Vector(-550, -950), Vector(-450, -800), Vector(-280, -400),
                                 Vector(90, -150), Vector(660, -140), Vector(1000, -180),
                                 Vector(1020, -100), Vector(640, 200), Vector(480, 420),
                                 Vector(480, 750), Vector(110, 620), Vector(-360, 560),
                                 Vector(-1020, 600), Vector(-1180, 520), Vector(-890, 410),
                                 Vector(-660, 170), Vector(-560, -180), Vector(-650, -700), ]))
