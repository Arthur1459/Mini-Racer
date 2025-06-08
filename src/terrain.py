import config as cf
import tools as t
import utils as u
from vector import *
import vars as vr
from math import cos, sin
from visuals import start_line

import pygame as pg

class Triangle:
    def __init__(self, p1: Vector, p2: Vector, p3: Vector):
        self.p1, self.p2, self.p3 = p1, p2, p3

    def get_points(self) -> tuple[Vector, Vector, Vector]: return self.p1, self.p2, self.p3
    def get_point_as_tuple(self): return tuple(self.p1()), tuple(self.p2()), tuple(self.p3())
    def intersect(self, point: Vector) -> bool:
        v1, v2, v3 = self.p1 - point, self.p2 - point, self.p3 - point
        return t.s(v1.dot(v2)) == t.s(v2.dot(v3)) == -1 or t.s(v2.dot(v3)) == t.s(v3.dot(v1)) == -1 or t.s(v3.dot(v1)) == t.s(v1.dot(v2)) == -1

class Rectangle:
    def __init__(self, size: Size, centered=True, angle=0):
        self.size = size
        self.angle = angle
        if not centered:
            self.t1 = Triangle(u.RotateVector(Vector(0, 0), angle),
                               u.RotateVector(Vector(0, size.y), angle),
                               u.RotateVector(Vector(size.x, size.y), angle))
            self.t2 = Triangle(u.RotateVector(Vector(0, 0), angle),
                               u.RotateVector(Vector(size.x, 0), angle),
                               u.RotateVector(Vector(size.x, size.y), angle))
        else:
            self.t1 = Triangle(u.RotateVector(Vector(-size.x/2, -size.y/2), angle),
                               u.RotateVector(Vector(-size.x/2, size.y/2), angle),
                               u.RotateVector(Vector(size.x/2, size.y/2), angle))
            self.t2 = Triangle(u.RotateVector(Vector(-size.x/2, -size.y/2), angle),
                               u.RotateVector(Vector(size.x/2, -size.y/2), angle),
                               u.RotateVector(Vector(size.x/2, size.y/2), angle))

        self.points = tuple((self.t1.p1(), self.t2.p2(), self.t2.p3(), self.t1.p2()))
        self.left = (self.t1.p1, self.t2.p2)
        self.right = (self.t2.p3(), self.t1.p2())

    def get_points(self) -> tuple: return self.points
    def intersect(self, point: Vector | tuple[int | float, int | float] | list[int | float]) -> bool:
        return self.t1.intersect(point) or self.t2.intersect(point)

class Polygone:
    def __init__(self, relative_points: list[Vector]):
        self.id = u.getNewId()
        self.points = relative_points

    def get_points(self) -> list[Vector]: return self.points
    def intersect(self, tested_point: Vector | list[Vector]):
        # Handle single point or list of points
        if isinstance(tested_point, Vector):
            # Single point
            px, py = tested_point()
            inside = False
            n = len(self.points)
            for i in range(n):
                x1, y1 = self.points[i]()
                x2, y2 = self.points[(i + 1) % n]()
                if (y1 > py) != (y2 > py):
                    x_intersect = (x2 - x1) * (py - y1) / (y2 - y1 + 1e-10) + x1
                    if px < x_intersect:
                        inside = not inside
            return inside

        elif isinstance(tested_point, (list, tuple)) and isinstance(tested_point[0], Vector):
            # List of points
            insides = [False for _ in range(len(tested_point))]
            for i in range(len(self.points)):
                x1, y1 = self.points[i]()
                x2, y2 = self.points[(i + 1) % len(self.points)]()
                for p_index, p in enumerate(tested_point):
                    if (y1 > p.y) != (y2 > p.y):
                        x_intersect = (x2 - x1) * (p.y - y1) / (y2 - y1 + 1e-10) + x1
                        if p.x < x_intersect:
                            insides[p_index] = not insides[p_index]
            return insides

        else:
            raise TypeError("Polygone intersection : point must be a vector (x, y) or tuple / list of (x, y) vectors.")

class Terrain:
    def __init__(self, world_position: Vector, shape):
        self.id = u.getNewId()
        self.tags = {'terrain'}

        self.world_position = world_position
        self.area = shape
        self.color = (100, 100, 100)
        self.owner = None

    def touch(self, point):
        if isinstance(point, Vector):
            return self.area.intersect(point - self.world_position)
        elif isinstance(point, list) and isinstance(point[0], Vector):
            return self.area.intersect([p - self.world_position for p in point])
        else:
            printWarning(f"[TERRAIN TOUCH] Incompatible argument : {point}")
            return False

    def update(self, movement=None):
        if movement is not None:
            self.world_position = self.world_position + movement
        self.draw()

    def draw(self):
        pg.draw.polygon(vr.game_window, self.color, [vr.world.ingame_position(self.world_position + relative_point) for relative_point in self.area.get_points()])

class RoadTile(Terrain):
    def __init__(self, world_position: Vector, width=200, length=200, angle=0, kerbs=(False, False)):
        super().__init__(world_position, Rectangle(Size(length, width), centered=True, angle=angle))
        self.direction = Vector(define_by_angle=True, angle=angle, norm=1)
        self.kerbs = kerbs
        self.lines = self.area.left, self.area.right
        self.tags.add('road')

    def draw(self, turn_shaker=False):
        pg.draw.polygon(vr.game_window, (80, 80, 80), [vr.world.ingame_position(self.world_position + relative_point) for relative_point in self.area.get_points()])
        for start, end in self.lines:
            pg.draw.line(vr.game_window, (100, 100, 100), vr.world.ingame_position(self.world_position + start), vr.world.ingame_position(self.world_position + end), width=self.area.size.width()//15)

        if self.kerbs[0]:
            pg.draw.line(vr.game_window, (100, 0, 0),
                         vr.world.ingame_position(self.world_position + self.lines[0][0] - self.direction * self.area.size.length()/8),
                         vr.world.ingame_position(self.world_position + self.lines[0][0] + self.direction * self.area.size.length()/8),
                         width=self.area.size.width()//15)
        if self.kerbs[1]:
            pg.draw.line(vr.game_window, (100, 0, 0),
                         vr.world.ingame_position(self.world_position + self.lines[1][1] - self.direction * self.area.size.length()/8),
                         vr.world.ingame_position(self.world_position + self.lines[1][1] + self.direction * self.area.size.length()/8),
                         width=self.area.size.width()//15)

class RoadStartTile(RoadTile):
    def __init__(self, *args):
        super().__init__(*args)
        scale = self.area.size.width() / start_line.get_size()[0]

        strat_line_size = Vector(self.area.size.width(), start_line.get_size()[1] * scale)
        self.start_line_visual, self.start_line_blit_pos = u.Rotate(pg.transform.scale(start_line, strat_line_size()), degrees(self.area.angle) - 90, center=(0, 0), pivot_from_topleft=(strat_line_size/2)())

    def draw(self, turn_shaker=False):
        super().draw()
        vr.game_window.blit(self.start_line_visual, vr.world.ingame_position(self.world_position + self.start_line_blit_pos))

class Road:
    def __init__(self, world_anchor: Vector, width=300):
        self.id = u.getNewId()
        self.tiles: list[RoadTile] = []
        self.world_anchor: Vector = world_anchor
        self.width = width
        self.total_length = 0
        self.nb_tiles = len(self.tiles)

    def update(self):
        for tile in self.tiles:
            if t.distance(tile.world_position, vr.race.player.world_position) > vr.world.game_size.radius() * (0.6 if vr.camera_lock else 1.) + tile.area.size.length(): continue
            tile.update()

    def get_position(self, world_position: Vector, last_position) -> int:
        for i in ((last_position - 1) % self.nb_tiles, last_position, (last_position + 1) % self.nb_tiles):
            if self.tiles[i].touch(world_position): return i
        index, m = 0, float('inf')
        for i in ((last_position - 1) % self.nb_tiles, last_position, (last_position + 1) % self.nb_tiles):
            m_ = t.distance(world_position(), self.tiles[i].world_position())
            if m_ < m:
                m, index = m_, i
        return index

    def next_tile(self, position) -> RoadTile:
        return self.tiles[(position + 1) % len(self.tiles)]
    def get_tile(self, position) -> RoadTile:
        return self.tiles[position % len(self.tiles)]
    def previous_tile(self, position) -> RoadTile:
        return self.tiles[(position - 1) % len(self.tiles)]

    def touch(self, point):
        for tile in self.tiles:
            if tile.touch(point): return True
        return False

    def addRoad(self, length, angle, width=None, forward=True, kerbs=(False, False)):
        width = width if width is not None else self.width
        if len(self.tiles) == 0:
            self.tiles.append(RoadStartTile(self.world_anchor, width, length, angle, kerbs))
        else:
            if forward:
                new_tile_connection_point = self.tiles[-1].world_position + self.tiles[-1].direction * max(0, (self.tiles[-1].area.size.length() - length)) * 0.5
                new_tile = RoadTile(NullVector(), length=length, angle=angle, width=(width if width is not None else self.width), kerbs=kerbs)
                new_tile.world_position = new_tile_connection_point + new_tile.direction * new_tile.area.size.length() * 0.5
                self.tiles.append(new_tile)
            else:
                new_tile_connection_point = self.tiles[-1].world_position - self.tiles[-1].direction * self.tiles[-1].area.size.length() * 0.5 * self.tiles[-1].area.size.length()/self.tiles[-1].area.size.width()
                new_tile = RoadTile(NullVector(), length=length, angle=angle,width=(width if width is not None else self.width), kerbs=kerbs)
                new_tile.world_position = new_tile_connection_point - new_tile.direction * new_tile.area.size.length() * 0.5
                self.tiles.insert(0,new_tile)
        self.total_length += length
        self.nb_tiles = len(self.tiles)

    def addStraight(self, length, angle=None):
        self.addRoad(length, rad(angle) if angle is not None else (self.tiles[-1].area.angle if len(self.tiles) > 0 else 0))

    def addTurn(self, angle, da=10, dl=100, base_angle=None):
        base_angle = base_angle if base_angle is not None else (self.tiles[-1].area.angle if len(self.tiles) > 0 else 0)
        kerbs = (False, False)
        if angle < 0: kerbs = (True, False)
        if angle > 0: kerbs = (False, True)
        for i in range(1, abs(angle//da) + 1):
            self.addRoad(dl, base_angle + t.s(angle) * rad(da) * i, kerbs=kerbs)
        self.addRoad(dl, base_angle + rad(angle))

class Block(Terrain):
    def __init__(self, world_position: Vector, relative_points: list[Vector]):
        super().__init__(world_position, Polygone(relative_points))
        self.color = (20, 20, 20)

class InvisibleBlock(Terrain):
    def __init__(self, world_position: Vector, relative_points: list[Vector], show=False, owner=None):
        super().__init__(world_position, Polygone(relative_points))
        self.color = (200, 200, 200)
        self.show = show
        self.owner = owner

    def draw(self):
        if self.show:
            super().draw()
