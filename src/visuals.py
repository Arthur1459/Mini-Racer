import time
import pygame.image as pgi
import pygame.transform as pgt
from pygame import font
from glob import glob

import config as cf
from utils import resource_path as path
import vars as vr


def img(filepath, resize=None, full_path=False, flip=(False, False)):
    img_raw = pgt.flip(pgi.load(filepath if full_path else path(f"rsc/visuals/{filepath}")), flip[0], flip[1])
    if resize is None:
        return img_raw
    else:
        return pgt.scale(img_raw, resize)

def load_folder(folderpath, resize=None, files_type="*.png", flip=(False, False)):
    files_paths = glob(path(f"rsc/visuals/{folderpath}/{files_type}"))
    return [img(filepath, full_path=True, resize=resize, flip=flip) for filepath in sorted(files_paths)]

class Animation:
    def __init__(self, name, folder, frame_duration=0.1, resize=None, flip=(False, False)):
        self.name = name
        self.flip = flip
        self.frames = load_folder(folder, resize=resize, flip=self.flip)
        self.frame_duration, self.t = frame_duration, vr.t
        self.index = 0

    def get_frame(self):
        self.update()
        return pgt.flip(self.frames[self.index], *self.flip)

    def setflip(self, flipx, flipy): self.flip = (flipx, flipy)

    def resize(self, size):
        self.frames = [pgt.scale(frame, size) for frame in self.frames]

    def update(self):
        if (vr.t - self.t) > self.frame_duration:
            self.index = (self.index + 1) % len(self.frames)

empty = img("empty.png")
start_line = img("start_line.png")
crown = img("crown.png", resize=(cf.racer_size[0] / 2, cf.racer_size[1] / 2))

racer_visuals = {'straight': Animation('straight', 'racer/straight', 0.1, resize=cf.racer_size, flip=(False, False)),
                 'turn_low': Animation('turn_low', 'racer/turn_low', 0.1, resize=cf.racer_size, flip=(False, False)),
                 'turn_high': Animation('turn_high', 'racer/turn_high', 0.1, resize=cf.racer_size, flip=(False, False))}
bot_visuals = {'straight': Animation('straight', 'bot/straight', 0.1, resize=cf.racer_size, flip=(False, False)),
                 'turn_low': Animation('turn_low', 'bot/turn_low', 0.1, resize=cf.racer_size, flip=(False, False)),
                 'turn_high': Animation('turn_high', 'bot/turn_high', 0.1, resize=cf.racer_size, flip=(False, False))}


