# Game configuration (Must be non-mutable)

game_name = "Mini Racer"
version = 1.0

window_default_size = (1280, 720)
game_scale = 2
fov = 1.3
game_resolution = (fov * game_scale * window_default_size[0], fov * game_scale * window_default_size[1])
scale = fov * game_scale
fullscreen = True
fps, dt = 60, 1/60
fps_threshold = 0.5
joystick = True

world_size = (16 * 2560, 16 * 1440)
racer_size = (74, 48) #(94, 62)
racer_radius = (racer_size[0]**2 + racer_size[1]**2)**0.5

