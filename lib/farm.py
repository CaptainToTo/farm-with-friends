import lib.crop
import lib.player

# contains the game state
class Farm:
    def __init__(self, width, height):
        self.players = {}
        self.grid = [[{'players': {}, 'crop': None} for j in range(width)] for i in range(height)]
        self.width = width
        self.height = height

    def is_valid_coord(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width
    
    def is_next_to_player(self, id, row, col):
        player = self.get_player(id)
        return ((row == player.row - 1 or row == player.row + 1) and col == player.col) or \
                ((col == player.col - 1 or col == player.col + 1) and row == player.row)
    
    def __str__(self):
        result = ""
        for row in self.grid:
            for col in row:
                if (len(col['players']) > 0):
                    result += " * "
                else:
                    result += f'   '
            result += "\n"
            for col in row:
                if (col['crop'] is None):
                    result += "[ ]"
                else:
                    result += f'[{str(col['crop'])}]'
            result += "\n"
        return result
    
    # player methods

    def add_player(self, id, username, row, col):
        self.players[id] = lib.player.Player(id, username, row, col)
        self.set_player_pos(id, row, col)
    
    def has_player(self, username):
        for id in self.players:
            if self.players[id].username == username:
                return True
        return False

    def get_player(self, id):
        return self.players[id]
    
    def get_players(self, row, col):
        players = []
        for id in self.grid[row][col]['players']:
            players.append(self.players[id])
        return players
    
    def remove_player(self, id):
        self.remove_player_pos(id)
        self.players.pop(id)

    # move player

    def set_player_pos(self, id, row, col):
        player = self.players[id]
        self.grid[row][col]['players'][id] = player
        player.row = row
        player.col = col
    
    def remove_player_pos(self, id):
        player = self.players[id]
        self.grid[player.row][player.col]['players'].pop(id)
        player.row = -1
        player.col = -1
    
    def move_player_to(self, id, row, col):
        self.remove_player_pos(id)
        self.set_player_pos(id, row, col)

    # planting and harvesting

    def plant_crop(self, crop_type, growth, row, col):
        self.grid[row][col]['crop'] = lib.crop.Crop(crop_type, growth)
    
    def get_crop(self, row, col):
        return self.grid[row][col]['crop']
    
    def get_crops(self):
        crops = []
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                if self.grid[row][col]['crop'] is not None:
                    crops.append((self.grid[row][col]['crop'], row, col))
        return crops
    
    def cell_empty(self, row, col):
        return self.get_crop(row, col) is None
    
    def harvest_crop(self, row, col):
        price = self.get_crop(row, col).price()
        self.grid[row][col]['crop'] = None
        return price