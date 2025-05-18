import pygame as pg
from math import cos, sin, pi, tan
import tools as t
import utils as u
import vars as vr
import config as cf
import time

from src.vars import world
from vector import Size, Vector
from racer import Racer, BotRacer
from world import World
from terrain import *
from race import Race

def init():

    pg.init()
    pg.display.set_caption(cf.game_name)

    # screen initialisation
    if not cf.fullscreen:
        vr.window = pg.display.set_mode(cf.window_default_size)
    else:
        vr.window = pg.display.set_mode(cf.window_default_size, pg.RESIZABLE, vsync=True)
        vr.window_size = vr.window.get_size()

    vr.game_window = pg.Surface(cf.game_resolution)
    vr.clock = pg.time.Clock()

    vr.world = World(Size(*cf.world_size), Vector(*vr.middle))
    vr.race = Race(nb_bots=19)
    return

def main():
    init()

    vr.running = True

    frames_fps, t_fps = 0, time.time() - 1

    while vr.running:

        vr.clock.tick(cf.fps)

        vr.t += cf.dt
        frames_fps += 1
        vr.fps = frames_fps/(time.time() - t_fps)
        if frames_fps > 1000:
            frames_fps, t_fps = 0, time.time()

        vr.inputs['CLICK'] = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                vr.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                print("Cursor : ", pg.mouse.get_pos(), f"(from center {Vector(*pg.mouse.get_pos()) - vr.world.ingame_middle()/2})")
                vr.inputs['CLICK'] = True

        # Main Loop #
        pre_update()
        if vr.fps > cf.fps * cf.fps_threshold:
            u.getInputs()
            update()
        post_update()
        # --------- #

    return

def update():
    vr.cursor_world = vr.world.world_position(cf.scale * Vector(*pg.mouse.get_pos()))

    vr.race.update()

    return

def pre_update():
    vr.game_window.fill((0, 50, 0))

def post_update():
    u.Text(str(round(vr.fps, 1)), (10, vr.gwin_height - 26), 24, 'orange')

    vr.window.blit(pg.transform.scale(vr.game_window, vr.window.get_size()), (0, 0))

    pg.display.update()
    return

if __name__ == "__main__":
    main()