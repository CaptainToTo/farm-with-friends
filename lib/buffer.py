
# used to concat RPCs into a single package. RPCs are separated by a '0xff' byte
class Buffer:
    def __init__(self):
        self.bytes = bytes()
        self.is_empty = True
    
    def add(self, rpc):
        self.bytes = self.bytes + rpc + bytes((0xff,))
        self.is_empty = False

    def get_rpcs(received):
        return received.split(bytes((0xff,)))

    def get_buffer(self):
        return self.bytes

    def reset_buffer(self):
        self.bytes = bytes()
        self.is_empty = True