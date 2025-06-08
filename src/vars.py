# Global variables used by the game
import config as cf


window_size = cf.window_default_size
win_width, win_height = window_size
win_middle = win_width/2, win_height/2

gwindow_size = cf.game_resolution
gwin_width, gwin_height = gwindow_size
middle = (gwin_width // 2, gwin_height // 2)

window = None
virtual_window = None
game_window = None
hud_window = None
clock = None

running = False

# In game
inputs = {}
fps = cf.fps
t = 0

cursor_world = (0, 0)
info_txt = ""
id = 0

# Elements
joystick = None
test = []
world = None
race = None
racer = None
terrain = []
road = None
bots = []

#
camera_lock = False
wait_key = 0
