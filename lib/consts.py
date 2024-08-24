# game dimensions
FARM_WIDTH  = 20
FARM_HEIGHT = 10

# server rules
MAX_PLAYERS = 4

# crops
CARROTS     = 0
ONIONS      = 1
TOMATOES    = 2
GRAPES      = 3
WATERMELON  = 4

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