# Global variables used by the game
import config as cf

gwindow_size = cf.game_resolution
gwin_width, gwin_height = gwindow_size
middle = (gwin_width // 2, gwin_height // 2)

window = None
game_window = None
clock = None

running = False

# In game
inputs = {}
fps = cf.fps
t = 0

cursor = (0, 0)
info_txt = ""
id = 0

# Elements
test = []
world = None
race = None
racer = None
terrain = []
road = None
bots = []

