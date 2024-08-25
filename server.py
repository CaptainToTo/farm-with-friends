import mysql.connector
import lib.consts
import lib.farm
import socket
import lib.protocols
import select
import time

def broadcast(player_list, data):
    for player in player_list:
        player.send(data)

# load database

password = input("database password: ")

db = mysql.connector.connect(
    host="localhost",
    user="root",        # TODO: replace with different user if applicable
    password=password,
    database="Farm"
)

cursor = db.cursor()

# load farm grid
cursor.execute("SELECT * FROM Crops")
grid_save = cursor.fetchall()

# game map contains server authoritative game state
game_map = lib.farm.Farm(lib.consts.FARM_WIDTH, lib.consts.FARM_HEIGHT)

for crop_save in grid_save:
    coords = lib.farm.deserialize_coords(crop_save[0])
    game_map.plant_crop(crop_save[1], crop_save[2], coords[0], coords[1])

# open server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', lib.consts.SERVER_PORT))
server.listen(lib.consts.MAX_PLAYERS)
read_list = [server]

# maps client sockets to player data
players = {}

last_tick = time.time()

# simulation loop
while True:
    # uses select to control tick speed, sort of
    readable, writable, errored = select.select(read_list, [], [], lib.consts.TICK_FREQ)
    new_tick = time.time()
    delta = new_tick - last_tick

    # receive input from clients
    for s in readable:
        # if receiving on the server socket, this is a new player connecting
        if s is server:
            client, addr = server.accept()
            read_list.append(client)

            # player login
            username = client.recv(1024).decode()

            # load player, or create a new player if the username doesn't exist in the database
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            player_save = cursor.fetchall()
            if (len(player_save) == 0):
                cursor.execute("INSERT INTO Users (username, pos_x, pos_y) VALUES (%s, 0, 0)", (username,))
                cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
                player_save = cursor.fetchall()
            
            id, name, row, col = player_save[0]
            
            # associate client socket to player id
            players[client] = id
            print(f"{username} joined the game ({row}, {col})")
            
            # add player to game
            game_map.add_player(id, name, row, col)
            broadcast(players, lib.protocols.add_player_rpc_encode(id, name, row, col))

            # send new player current game state
            for player in game_map.players.values():
                if player.id != id:
                    client.send(lib.protocols.add_player_rpc_encode(player.id, player.username, player.row, player.col))
            for crop_obj in game_map.get_crops():
                crop, crop_row, crop_col = crop_obj
                client.send(lib.protocols.plant_crop_rpc_encode(crop.crop_type, crop.growth, crop_row, crop_col))
        
        # currently connected player is sending input
        else:
            data = s.recv(1024)
            id = players[s]
            player = game_map.get_player(id)

            # apply player input and send state update
            rpc_id, args = lib.protocols.decode_client_rpc(data)

            try:
                if rpc_id == lib.protocols.MOVE_INPUT_RPC_ID:
                    row, col = args
                    if not (game_map.is_valid_coord(row, col) and game_map.is_next_to_player(id, row, col)):
                        print(player.row, player.col, row, col)
                        raise ValueError(lib.protocols.MOVE_INPUT_RPC_ID)
                    game_map.move_player_to(id, row, col)
                    broadcast(players, lib.protocols.move_player_rpc_encode(id, row, col))
                
                elif rpc_id == lib.protocols.PLANT_INPUT_RPC_ID:
                    crop_type = args[0]
                    if not (lib.consts.is_crop_type(crop_type) and game_map.cell_empty(player.row, player.col)):
                        raise ValueError(lib.protocols.PLANT_INPUT_RPC_ID)
                    game_map.plant_crop(crop_type, 0, player.row, player.col)
                    growth = game_map.get_crop(player.row, player.col).growth
                    broadcast(players, lib.protocols.plant_crop_rpc_encode(crop_type, growth, player.row, player.col))
                
                elif rpc_id == lib.protocols.HARVEST_INPUT_RPC_ID:
                    if game_map.cell_empty(player.row, player.col):
                        raise ValueError(lib.protocols.PLANT_INPUT_RPC_ID)
                    game_map.harvest_crop(player.row, player.col)
                    broadcast(players, lib.protocols.harvest_crop_rpc_encode(player.row, player.col))
            
            # handle faulty rpc composition
            except ValueError as err:
                # enforce player position to correct de-sync
                if err.args[0] == lib.protocols.MOVE_INPUT_RPC_ID:
                    broadcast(players, lib.protocols.move_player_rpc_encode(id, player.row, player.col))

                print("faulty rpc received from " + game_map.get_player(players[s]).username)

    # update crop growth, crop object is a tuple (Crop instance, row, col)
    for crop_obj in game_map.get_crops():
        crop, row, col = crop_obj
        crop.grow(delta)
        # send update to clients
        broadcast(players, lib.protocols.crop_grow_rpc_encode(crop.growth, row, col))

    last_tick = new_tick
