import lib.consts

class Crop:
    def __init__(self, crop_type, growth):
        self.crop_type = crop_type
        self.growth = growth
    
    # get the display character for the game
    def __str__(self):
        return lib.consts.CROP_CHAR[self.crop_type]
    
    def price(self):
        return int(self.growth * lib.consts.CROP_PROFIT_MULT[self.crop_type])
    
    def grow(self, delta):
        self.growth = min(lib.consts.MAX_GROWTH, self.growth + (delta * lib.consts.CROP_GROWTH_MULT[self.crop_type]))