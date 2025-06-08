import pygame as pg
from math import cos, sin, pi, tan

from freetype import FT_GlyphRec

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
    pg.joystick.init()
    print("Joystics connected : ", pg.joystick.get_count())

    # screen initialisation
    if not cf.fullscreen:
        vr.window = pg.display.set_mode(cf.window_default_size)
    else:
        vr.window = pg.display.set_mode(cf.window_default_size, pg.RESIZABLE, vsync=True)
        vr.window_size = vr.window.get_size()

    vr.virtual_window = pg.Surface(cf.window_default_size)
    vr.game_window = pg.Surface(cf.game_resolution)
    vr.hud_window = pg.Surface(cf.window_default_size, pg.SRCALPHA)
    vr.clock = pg.time.Clock()

    vr.world = World(Size(*cf.world_size), Vector(*vr.middle))
    vr.race = Race(nb_bots=10)
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
            # Handle hotplugging
            elif event.type == pg.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                vr.joystick = pg.joystick.Joystick(event.device_index)
                print(f"Joystick {vr.joystick.get_instance_id()} connected")
            elif event.type == pg.JOYDEVICEREMOVED:
                vr.joystick = None
                print(f"Joystick disconnected")

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
    if vr.inputs['Y'] and u.waitkey(): vr.camera_lock = False if vr.camera_lock else True
    vr.race.update()
    
    return

def pre_update():
    vr.game_window.fill((0, 50, 0))
    vr.hud_window.fill((0, 50, 0, 1))

def post_update():
    u.Text(str(round(vr.fps, 1)), (10, vr.win_height - 16), 12, 'orange')

    if vr.camera_lock:
        rotated, blit_pos = u.Rotate(pg.transform.scale(vr.game_window, (Vector(*vr.virtual_window.get_size())*1.5)()), -deg(vr.race.player.angle)-90, (1.5 * Vector(*vr.virtual_window.get_size())/2)(), (1.5 * Vector(*vr.virtual_window.get_size())/2)())
        vr.virtual_window.blit(rotated, (Vector(*blit_pos) - Vector(*vr.virtual_window.get_size())/4)())
    else:
        vr.virtual_window.blit(pg.transform.scale(vr.game_window, vr.virtual_window.get_size()), (0, 0))
    vr.virtual_window.blit(pg.transform.scale(vr.hud_window, vr.virtual_window.get_size()), (0, 0))
    vr.window.blit(pg.transform.scale(vr.virtual_window, vr.window.get_size()), (0, 0))
    pg.display.update()
    return

if __name__ == "__main__":
    main()