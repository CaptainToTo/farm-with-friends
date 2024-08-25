import mysql.connector
import lib.buffer
import lib.consts
import lib.farm
import socket
import lib.protocols
import select
import time
import server_lib.db

def broadcast(player_list, data):
    for player in player_list:
        id, buffer = player_list[player]
        buffer.add(data)

# load database

password = input("database password: ")

db = server_lib.db.Database(password)

# load farm grid
grid_save = db.get_crops()
profit = db.get_profit()

# game map contains server authoritative game state
game_map = lib.farm.Farm(lib.consts.FARM_WIDTH, lib.consts.FARM_HEIGHT)

for crop_save in grid_save:
    coords = server_lib.db.deserialize_coords(crop_save[0])
    # crop_type, growth, row, col
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

            # player login
            username = client.recv(lib.consts.BUFFER_SIZE).decode()

            # reject if player is already logged in
            if game_map.has_player(username):
                client.close()
                continue

            # load player, or create a new player if the username doesn't exist in the database            
            id, name, row, col = db.login_player(username)
            read_list.append(client)

            # each player gets a buffer
            buffer = lib.buffer.Buffer()
            
            # associate client socket to player id
            players[client] = (id, buffer)
            print(f"{username} joined the game ({row}, {col})")
            
            # add player to game
            game_map.add_player(id, name, row, col)
            broadcast(players, lib.protocols.add_player_rpc_encode(id, name, row, col))

            # send new player current game state
            for player in game_map.players.values():
                if player.id != id:
                    buffer.add(lib.protocols.add_player_rpc_encode(player.id, player.username, player.row, player.col))
            for crop_obj in game_map.get_crops():
                crop, crop_row, crop_col = crop_obj
                buffer.add(lib.protocols.plant_crop_rpc_encode(crop.crop_type, crop.growth, crop_row, crop_col))
        
        # currently connected player is sending input
        else:
            data = None
            try:
                data = s.recv(lib.consts.BUFFER_SIZE)
            except:
                pass
            id, buffer = players[s]
            player = game_map.get_player(id)

            # player has disconnected
            if not data:
                print(f"{player.username} has left the game")
                players.pop(s)
                game_map.remove_player(id)
                read_list.remove(s)
                s.close()
                broadcast(players, lib.protocols.remove_player_rpc_encode(id))
                continue


            # apply player input and send state update
            rpc_id, args = lib.protocols.decode_client_rpc(data)

            try:
                if rpc_id == lib.protocols.MOVE_INPUT_RPC_ID:
                    row, col = args
                    if not (game_map.is_valid_coord(row, col) and game_map.is_next_to_player(id, row, col)):
                        raise ValueError(lib.protocols.MOVE_INPUT_RPC_ID)
                    game_map.move_player_to(id, row, col)
                    broadcast(players, lib.protocols.move_player_rpc_encode(id, row, col))
                    db.move_player(id, row, col)
                    print(f"{player.username} moved to ({row}, {col})")
                
                elif rpc_id == lib.protocols.PLANT_INPUT_RPC_ID:
                    crop_type = args[0]
                    if not (lib.consts.is_crop_type(crop_type) and game_map.cell_empty(player.row, player.col)):
                        raise ValueError(lib.protocols.PLANT_INPUT_RPC_ID)
                    game_map.plant_crop(crop_type, 0, player.row, player.col)
                    growth = game_map.get_crop(player.row, player.col).growth
                    broadcast(players, lib.protocols.plant_crop_rpc_encode(crop_type, growth, player.row, player.col))
                    db.add_crop(crop_type, growth, player.row, player.col)
                    print(f"{player.username} planted a '{str(game_map.get_crop(player.row, player.col))}' at ({player.row}, {player.col})")
                
                elif rpc_id == lib.protocols.HARVEST_INPUT_RPC_ID:
                    if game_map.cell_empty(player.row, player.col):
                        raise ValueError(lib.protocols.PLANT_INPUT_RPC_ID)
                    profit = min(lib.consts.MAX_PROFIT, profit + game_map.harvest_crop(player.row, player.col))
                    broadcast(players, lib.protocols.harvest_crop_rpc_encode(profit, player.row, player.col))
                    db.remove_crop(profit, player.row, player.col)
                    print(f"{player.username} harvested at ({player.row}, {player.col}), profits are now {profit}")
            
            # handle faulty rpc composition
            except ValueError as err:
                # enforce state to correct de-sync
                if err.args[0] == lib.protocols.MOVE_INPUT_RPC_ID:
                    broadcast(players, lib.protocols.move_player_rpc_encode(id, player.row, player.col))
                
                elif err.args[0] == lib.protocols.PLANT_INPUT_RPC_ID:
                    crop = game_map.get_crop(player.row, player.col)
                    buffer.add(lib.protocols.plant_crop_rpc_encode(crop.crop_type, crop.growth, player.row, player.col))
                
                elif err.args[0] == lib.protocols.HARVEST_INPUT_RPC_ID:
                    buffer.add(lib.protocols.harvest_crop_rpc_encode(player.row, player.col))

                print("faulty rpc received from " + game_map.get_player(id).username)

    # update crop growth, crop object is a tuple (Crop instance, row, col)
    for crop_obj in game_map.get_crops():
        crop, row, col = crop_obj
        crop.grow(delta)
        # send update to clients
        broadcast(players, lib.protocols.crop_grow_rpc_encode(crop.growth, row, col))
        db.set_crop_growth(crop.growth, row, col)
    
    # send all non empty buffers
    for player in players:
        id, buffer = players[player]
        if not buffer.is_empty:
            player.send(buffer.get_buffer())
        # clear buffer for next tick
        buffer.reset_buffer()

    last_tick = new_tick
