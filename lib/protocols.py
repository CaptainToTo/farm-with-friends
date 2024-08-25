ADD_PLAYER_RPC_ID    = 0
REMOVE_PLAYER_RPC_ID = 1
MOVE_PLAYER_RPC_ID   = 2
PLANT_CROP_RPC_ID    = 3
HARVEST_CROP_RPC_ID  = 4
CROP_GROW_RPC_ID     = 5

MOVE_INPUT_RPC_ID    = 6
PLANT_INPUT_RPC_ID   = 7
HARVEST_INPUT_RPC_ID = 8

# return tuple (rpc id, (tuple of args)), run on client to decode RPCs from server
def decode_server_rpc(data):
    rpc_id = data[0]
    if rpc_id == ADD_PLAYER_RPC_ID:
        return (rpc_id, add_player_rpc_decode(data))
    elif rpc_id == REMOVE_PLAYER_RPC_ID:
        return (rpc_id, remove_player_rpc_decode(data))
    elif rpc_id == MOVE_PLAYER_RPC_ID:
        return (rpc_id, move_player_rpc_decode(data))
    elif rpc_id == PLANT_CROP_RPC_ID:
        return (rpc_id, plant_crop_rpc_decode(data))
    elif rpc_id == HARVEST_CROP_RPC_ID:
        return (rpc_id, harvest_crop_rpc_decode(data))
    elif rpc_id == CROP_GROW_RPC_ID:
        return (rpc_id, crop_grow_rpc_decode(data))
    return None

# return tuple (rpc id, (tuple of args)), run on server to decode RPCs from client
def decode_client_rpc(data):
    rpc_id = data[0]
    if rpc_id == MOVE_INPUT_RPC_ID:
        return (rpc_id, move_input_rpc_decode(data))
    elif rpc_id == PLANT_INPUT_RPC_ID:
        return (rpc_id, plant_input_rpc_decode(data))
    elif rpc_id == HARVEST_INPUT_RPC_ID:
        return (rpc_id, harvest_input_rpc_decode(data))
    return None

# add player rpc

def add_player_rpc_encode(id, username, row, col):
    return bytes((ADD_PLAYER_RPC_ID, id)) + username.encode() + '\0'.encode() + bytes((row, col))

def add_player_rpc_decode(data):
    player_id = data[1]
    username = ''
    i = 2
    while data[i] != 0:
        username += chr(data[i])
        i += 1
    row = data[i+1]
    col = data[i+2]
    return (player_id, username, row, col)

# remove player rpc

def remove_player_rpc_encode(id):
    return bytes((REMOVE_PLAYER_RPC_ID, id))

def remove_player_rpc_decode(data):
    return (data[1],)

# move player rpc

def move_player_rpc_encode(id, row, col):
    return bytes((MOVE_PLAYER_RPC_ID, id, row, col))

def move_player_rpc_decode(data):
    return (data[1], data[2], data[3])

# plant crop rpc

def plant_crop_rpc_encode(crop_type, growth, row, col):
    return bytes((PLANT_CROP_RPC_ID, crop_type, int(growth*10), row, col))

def plant_crop_rpc_decode(data):
    return (data[1], float(data[2])/10, data[3], data[4])

# harvest crop rpc

def harvest_crop_rpc_encode(profits: int, row, col):
    return bytes((HARVEST_CROP_RPC_ID,)) + profits.to_bytes(2, byteorder='big') + bytes((row, col))

def harvest_crop_rpc_decode(data):
    return (int.from_bytes(data[1:3], byteorder='big'), data[3], data[4])

# crop grow rpc

def crop_grow_rpc_encode(growth, row, col):
    return bytes((CROP_GROW_RPC_ID, int(growth*10), row, col))

def crop_grow_rpc_decode(data):
    return (float(data[1])/10, data[2], data[3])

# move input rpc

def move_input_rpc_encode(row, col):
    return bytes((MOVE_INPUT_RPC_ID, row, col))

def move_input_rpc_decode(data):
    return (data[1], data[2])

# plant input rpc

def plant_input_rpc_encode(plant_type):
    return bytes((PLANT_INPUT_RPC_ID, plant_type))

def plant_input_rpc_decode(data):
    return (data[1],)

# harvest input rpc

def harvest_input_rpc_encode():
    return bytes((HARVEST_INPUT_RPC_ID,))

def harvest_input_rpc_decode(data):
    return None