import mysql.connector
import lib.consts
import lib.farm

# load database

password = input("database password: ")

db = mysql.connector.connect(
    host="localhost",
    user="root",        # TODO: replace with different user if applicable
    password=password,
    database="Farm"
)

cursor = db.cursor()
cursor.execute("INSERT INTO Crops (coords, crop_type, growth) VALUES ('5x5', 0, 0)")
cursor.execute("SELECT * FROM Crops")
grid_save = cursor.fetchall()

game_map = lib.farm.Farm(lib.consts.FARM_WIDTH, lib.consts.FARM_HEIGHT)

for crop_save in grid_save:
    coords = lib.farm.deserialize_coords(crop_save[0])
    game_map.plant_crop(crop_save[1], crop_save[2], coords[0], coords[1])

print(game_map)