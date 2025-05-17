import os
import sys
import time
import pygame as pg
import random

import vars as vr
from logger import printWarning
from vector import Vector, rad, deg, sin, cos, NullVector

def evaluate_impact(func):
    def wrapper(*args):
        t0 = time.time()
        result = func(*args)
        dt = time.time() - t0
        print(f"Impact Evaluation : {(dt / 0.01667 * 100):.3f} % ({dt*1000:.2f} ms)")
        return result
    return wrapper

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    #print(os.path.join(base_path, relative_path))
    return os.path.join(base_path, relative_path)

pg.font.init()
text_fonts = {size: pg.font.Font(resource_path("rsc/misc/pixel.ttf"), size) for size in range(4, 81, 4)}

def Text(msg, coord, size, color):  # blit to the screen a text
    TextColor = pg.Color(color) # set the color of the text
    if size in text_fonts:
        font = text_fonts[size]
    else:
        printWarning(f"Size {size} not supported. (must be a multiple of 4 between 4 to 80)")
        font = text_fonts[24]
    return vr.game_window.blit(font.render(msg, True, TextColor), coord)  # return and blit the text on the screen

def getInputs():
    keys = pg.key.get_pressed()
    vr.inputs["SPACE"] = True if keys[pg.K_SPACE] else False

    vr.inputs["UP"] = True if (keys[pg.K_UP] or keys[pg.K_z]) else False
    vr.inputs["DOWN"] = True if (keys[pg.K_DOWN] or keys[pg.K_s]) else False
    vr.inputs["RIGHT"] = True if (keys[pg.K_RIGHT] or keys[pg.K_d]) else False
    vr.inputs["LEFT"] = True if (keys[pg.K_LEFT] or keys[pg.K_q]) else False

    vr.inputs["R"] = True if (keys[pg.K_r] or keys[pg.K_z]) else False

def angle_diff(angle_1, angle_2):
    return (angle_1 - angle_2 + 3.14) % (2 * 3.14) - 3.14

def Rotate(image, angle, center, pivot_from_topleft) -> (pg.Surface, tuple[float, float]):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(center[0] - pivot_from_topleft[0], center[1] - pivot_from_topleft[1]))
    offset_center_to_pivot = pg.math.Vector2(center) - image_rect.center

    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(angle)

    # roatetd image center
    rotated_image_center = (center[0] - rotated_offset.x, center[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pg.transform.rotate(image, -angle)
    x_blit, y_blit, _, _ = rotated_image.get_rect(center=rotated_image_center)

    return rotated_image, (x_blit, y_blit)


def RotateVector(v: Vector,
                 angle: float,
                 center: Vector = NullVector()) -> Vector:
    # Translate vector to origin
    dx, dy = (v - center)()

    cos_a = cos(angle)
    sin_a = sin(angle)

    # Apply rotation
    rotated_dx = dx * cos_a - dy * sin_a
    rotated_dy = dx * sin_a + dy * cos_a
    rotated_dp = Vector(rotated_dx, rotated_dy)
    result = center + rotated_dp
    return result

def isInWindow(coord):
    if 0 <= coord[0] <= vr.win_width:
        if 0 <= coord[1] <= vr.win_height:
            return True
    return False

def makeSeg(a, b):
    return lambda t: (b[0] + (t - 1) * (b[0] - a[0]), b[1] + (t - 1) * (b[1] - a[1]))

def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def drawSeg(seg):
    pg.draw.line(vr.window, (20, 20, 100), seg(0), seg(1), 4)

def getNewId():
    vr.id += 1
    return vr.id

def generate_name():
    consonants = [
        "b", "c", "d", "f", "g", "h", "j", "k", "l",
        "m", "n", "p", "r", "s", "t", "v", "x", "z"
    ]
    vowels = ["a", "e", "i", "o", "u", "y"]

    patterns = [
        "VCV", "CVC", "CVV", "CVCV", "CVVC", "VCVC"
    ]

    pattern = random.choice(patterns)
    name = ""
    for ch in pattern:
        if ch == "C":
            name += random.choice(consonants)
        elif ch == "V":
            name += random.choice(vowels)

    return name.capitalize()
