class Database:
    def __init__(self, password):
        if password == "na":
            self.is_dummy = True
            self.cur_id = 0
            self.player_data = {}
        else:
            import mysql.connector
            self.is_dummy = False
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",        # TODO: replace with different user if applicable
                password=password,
                database="Farm"
                )
            self.cursor = self.db.cursor()
            self.is_dirty = False
    
    def get_crops(self):
        if self.is_dummy:
            return []
        self.cursor.execute("SELECT * FROM Crops")
        return self.cursor.fetchall()
    
    def get_profit(self):
        if self.is_dummy:
            return 0
        self.cursor.execute("SELECT * FROM Profit")
        table = self.cursor.fetchall()
        return table[0][0]
    
    def login_player(self, username):
        if self.is_dummy:
            if username in self.player_data:
                return self.player_data[username]
            self.player_data[username] = (self.cur_id, username, 0, 0)
            self.cur_id += 1
            return self.player_data[username]

        self.cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        player_save = self.cursor.fetchall()
        if (len(player_save) == 0):
            self.cursor.execute("INSERT INTO Users (username, pos_row, pos_col) VALUES (%s, 0, 0)", (username,))
            self.cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            player_save = self.cursor.fetchall()
            self.is_dirty = True
            
        return player_save[0]
    
    def add_crop(self, crop_type, growth, row, col):
        if self.is_dummy:
            return
        self.cursor.execute(f"INSERT INTO Crops (coords, crop_type, growth) VALUES ('{serialize_coords(row, col)}', {crop_type}, {growth})")
        self.is_dirty = True
    
    def remove_crop(self, profit, row, col):
        if self.is_dummy:
            return
        self.cursor.execute(f"DELETE FROM Crops WHERE coords = '{serialize_coords(row, col)}'")
        self.cursor.execute(f"UPDATE Profit SET val = {profit}")
        self.is_dirty = True
    
    def move_player(self, id, row, col):
        if self.is_dummy:
            for user in self.player_data:
                if self.player_data[user][0] == id:
                    self.player_data[user] = (id, user, row, col)
                    return

        self.cursor.execute(f"UPDATE Users SET pos_row = {row}, pos_col = {col} WHERE id = {id}")
        self.is_dirty = True
    
    def set_crop_growth(self, growth, row, col):
        if self.is_dummy:
            return
        self.cursor.execute(f"UPDATE Crops SET growth = {growth} WHERE coords = '{serialize_coords(row, col)}'")
        self.is_dirty = True
    
    def save_changes(self):
        if self.is_dummy:
            return
        if self.is_dirty:
            self.db.commit()
        self.is_dirty = False


def deserialize_coords(val):
    coords_strs = val.split('x')
    return (int(coords_strs[0]), int(coords_strs[1]))

def serialize_coords(row, col):
    return f'{row}x{col}'