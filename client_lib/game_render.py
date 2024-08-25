import curses
from curses import wrapper

class Window:
    def __init__(self, width, height, inspector_height):
        self.true_width = width * 3
        self.true_height = height * 2

        self.top_farm = 1
        self.bottom_farm = self.true_height + 1
        self.right_farm = self.true_width
        self.left_farm = 1

        self.inspector_height = inspector_height

        self.top_inspector = self.bottom_farm + 2
        self.bottom_inspector = self.top_inspector + self.inspector_height - 1
        self.right_inspector = self.right_farm
        self.left_inspector = 1

def build_window(stdscr, width, height, inspector_height):
    # mult height and width based on character count used by Farm display
    rect = Window(width, height, inspector_height)

    stdscr.addstr('+' + ('-' * rect.true_width) + '+')
    stdscr.addstr(rect.bottom_farm + 1, 0, '+' + ('-' * rect.true_width) + '+')
    stdscr.addstr(rect.bottom_inspector + 1, 0, '+' + ('-' * rect.true_width) + '+')

    for i in range(rect.top_farm, rect.bottom_farm + 1):
        stdscr.addstr(i, 0, "|")
    for i in range(rect.top_farm, rect.bottom_farm + 1):
        stdscr.addstr(i, rect.right_farm + 1, "|")
    
    for i in range(rect.top_inspector, rect.bottom_inspector + 1):
        stdscr.addstr(i, 0, "|")
    for i in range(rect.top_inspector, rect.bottom_inspector + 1):
        stdscr.addstr(i, rect.right_farm + 1, "|")

    return rect

def display_farm(stdscr, rect, farm_str):
    lines = farm_str.split('\n')
    i = 0
    for line in lines:
        stdscr.addstr(rect.top_farm + i, rect.left_farm, line)
        i += 1

def display_players(stdscr, rect, players):
    players_title = "Players:"
    stdscr.addstr(rect.top_inspector, rect.right_inspector - len(players_title), players_title)
    i = rect.top_inspector + 1
    for player in players:
        stdscr.addstr(i, rect.right_inspector - len(player.username), player.username)
        i += 1

def display_cell(stdscr, rect, crop, row, col):
    stdscr.addstr(rect.top_inspector, rect.left_inspector, f"Cell: ({row + 1}, {col + 1})")
    stdscr.addstr(rect.top_inspector + 1, rect.left_inspector, f"Crop: {str(crop)}     ")
    stdscr.addstr(rect.top_inspector + 2, rect.left_inspector, f"Growth: {crop.growth if crop != None else "       "}")
