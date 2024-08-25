# game dimensions
FARM_WIDTH  = 20
FARM_HEIGHT = 10
INSPECTOR_HEIGHT = 5 # should be max players + 1

# server rules
MAX_PLAYERS = 4
SERVER_PORT = 8080
TICK_FREQ   = 0.1  # 10 fps, sort of
MAX_GROWTH  = 20   # this x10 can't be greater than 256
BUFFER_SIZE = 4096

# controls
UP       = 'w'
DOWN     = 's'
LEFT     = 'a'
RIGHT    = 'd'
INTERACT = 'e'

# crops
CARROTS     = 0
ONIONS      = 1
TOMATOES    = 2
GRAPES      = 3
WATERMELON  = 4

def is_crop_type(value):
    return CARROTS <= value <= WATERMELON

# crops characters
CROP_CHAR = [
    'C',
    'O',
    'T',
    'G',
    'W'
]

# multiply by delta time for growth increment
CROP_GROWTH_MULT = [
    0.5,
    0.7,
    0.4,
    0.9,
    0.3
]

# multiply by crop growth for price when sold
CROP_PROFIT_MULT = [
    3,
    2,
    3,
    1,
    5
]