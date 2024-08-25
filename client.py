import socket
import lib.consts
import lib.protocols
import client_lib.game_render
from curses import wrapper
import lib.crop
import lib.farm
import select

# login
local_username = input("username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', lib.consts.SERVER_PORT))
read_list = [client]

client.send(local_username.encode())

# client game map follows
game_map = lib.farm.Farm(lib.consts.FARM_WIDTH, lib.consts.FARM_HEIGHT)

def main(stdscr):
    # make it so getch is non-blocking
    stdscr.nodelay(True)

    # local player state
    local_id = -1
    local_player = None

    # simulation loop
    while True:
        readable, writable, errored = select.select(read_list, [], [], lib.consts.TICK_FREQ)

        for s in readable:
            if s is client:
                data = s.recv(1024)

                # apply state update from server
                try:
                    rpc_id, args = lib.protocols.decode_server_rpc(data)

                    if rpc_id == lib.protocols.ADD_PLAYER_RPC_ID:
                        id, username, row, col = args
                        game_map.add_player(id, username, row, col)

                        # save local player
                        if username == local_username:
                            local_id = id
                            local_player = game_map.get_player(id)
                    
                    elif rpc_id == lib.protocols.REMOVE_PLAYER_RPC_ID:
                        id = args[0]
                        game_map.remove_player(id)
                    
                    elif rpc_id == lib.protocols.MOVE_PLAYER_RPC_ID:
                        id, row, col = args
                        game_map.move_player_to(id, row, col)
                    
                    elif rpc_id == lib.protocols.PLANT_CROP_RPC_ID:
                        crop_type, growth, row, col = args
                        game_map.plant_crop(crop_type, growth, row, col)
                    
                    elif rpc_id == lib.protocols.HARVEST_CROP_RPC_ID:
                        row, col = args
                        game_map.harvest_crop(row, col)
                    
                    elif rpc_id == lib.protocols.CROP_GROW_RPC_ID:
                        growth, row, col = args
                        game_map.get_crop(row, col).growth = growth
                
                except:
                    pass
        
        # get player input
        char = stdscr.getch()

        # send input to server
        if char == ord(lib.consts.UP) and game_map.is_valid_coord(local_player.row - 1, local_player.col):
            client.send(lib.protocols.move_input_rpc_encode(local_player.row - 1, local_player.col))
        
        elif char == ord(lib.consts.DOWN) and game_map.is_valid_coord(local_player.row + 1, local_player.col):
            client.send(lib.protocols.move_input_rpc_encode(local_player.row + 1, local_player.col))
        
        elif char == ord(lib.consts.LEFT) and game_map.is_valid_coord(local_player.row, local_player.col - 1):
            client.send(lib.protocols.move_input_rpc_encode(local_player.row, local_player.col - 1))
        
        elif char == ord(lib.consts.RIGHT) and game_map.is_valid_coord(local_player.row, local_player.col + 1):
            client.send(lib.protocols.move_input_rpc_encode(local_player.row, local_player.col + 1))
        
        elif char == ord(lib.consts.INTERACT) and game_map.cell_empty(local_player.row, local_player.col):
            client.send(lib.protocols.plant_input_rpc_encode(lib.consts.CARROTS))
        
        elif char == ord(lib.consts.INTERACT) and not game_map.cell_empty(local_player.row, local_player.col):
            client.send(lib.protocols.harvest_input_rpc_encode())
        
        # render frame
        stdscr.clear()
        rect = client_lib.game_render.build_window(
            stdscr, 
            lib.consts.FARM_WIDTH, 
            lib.consts.FARM_HEIGHT, 
            lib.consts.INSPECTOR_HEIGHT
            )
        client_lib.game_render.display_farm(stdscr, rect, str(game_map))
        client_lib.game_render.display_players(
            stdscr, 
            rect, 
            game_map.get_players(local_player.row, local_player.col)
            )
        client_lib.game_render.display_cell(
            stdscr, 
            rect, 
            game_map.get_crop(local_player.row, local_player.col), 
            local_player.row, 
            local_player.col
            )
        stdscr.refresh()

# to render game with curses
wrapper(main)