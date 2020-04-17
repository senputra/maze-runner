import importlib
if __name__ == "__main__":
    spam_spec = importlib.util.find_spec("asciimatics")
    if spam_spec is None:
        # install necessary package
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "asciimatics"])

    from asciimatics.effects import Print
    from asciimatics.renderers import BarChart, FigletText, Fire, StaticRenderer
    from asciimatics.scene import Scene
    from asciimatics.screen import Screen
    from asciimatics.exceptions import NextScene, ResizeScreenError, StopApplication
    from asciimatics.event import KeyboardEvent
    from random import randint
    from libdw import sm
    from time import sleep
    import sys
    import math
    import time


class GPU():  # This class wrap asciimatics so that it can be replaced with any other TUI lib.

    __DISABLE_KEYBOARD_INTERRUPT = True

    def __init__(self):
        self.start()
        # put a character into a buffer that is as big as the terminal

    def print_at(self, char: str, x: int, y: int,  color=7, attr=0, bg=0, transparent=False) -> None:
        try:
            self.__screen.print_at(char, x, y, color, attr, bg, transparent)
        except:
            print("Screen is not asigned")

    def get_event(self):
        return self.__screen.get_event()

    # set the title of the window
    def set_title(self, title: str) -> None:
        self.__screen.set_title(title)

    # flush the buffer to the terminal window
    def refresh(self):
        self.__screen.refresh()

    # play the queued scene to the screen directly
    def playScene(self, effect_list, duration=-1, stop_on_resize=True, input_handler=None):
        self.__screen.play([Scene(effect_list, duration)], stop_on_resize=stop_on_resize,
                           unhandled_input=input_handler)

    def start(self):
        self.__screen = Screen.open(
            catch_interrupt=self.__DISABLE_KEYBOARD_INTERRUPT)

    # close the opened screen and clear buffer to prevent memmory leaks
    def shutdown(self, restore=True):
        self.__screen.close(restore=restore)

    @property
    def screen(self):
        return self.__screen

    @property
    def height(self):
        return self.__screen.height

    @property
    def width(self):
        return self.__screen.width


class Coordinate():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, distance, angle):
        self.x += math.cos(angle) * distance
        self.y += math.sin(angle) * distance

    @property
    def x_int(self):
        return int(self.x)

    @property
    def y_int(self):
        return int(self.y)


class StateMachine(sm.SM):
    start_state = {
        "START_TIME": None,
        "TIME_ELAPSED": 0,  # in second
        "DIFFICULTY": None,  # easy or hard
        "SCREEN": "MENU",  # Which screen the user is at
        "MAP_COUNTER": 0,
        "WIN": False,
    }

    def __screen_menu(self, state, inp_key_code):
        if inp_key_code in (ord("H"), ord("h")):
            state.update({
                "DIFFICULTY": "HARD",
                "SCREEN": "WAIT",
                "MAP_COUNTER": 5,
            })
        elif inp_key_code in (ord("E"), ord("e")):
            state.update({
                "DIFFICULTY": "EASY",
                "SCREEN": "WAIT",
                "MAP_COUNTER": 100,
            })
        elif inp_key_code in (ord("Q"), ord("q")):
            state.update({
                "SCREEN": "QUIT",
            })

        return state

    def __screen_wait(self, state, inp_key_code):
        if inp_key_code in (ord(" "), ord("\n")):
            state.update({
                "SCREEN": "PLAY",
                "START_TIME": time.time(),
            })
        return state

    def __screen_play(self, state, inp_key_code):

        if isinstance(inp_key_code, str):
            elapsed = time.time() - state["START_TIME"]
            state.update({
                "SCREEN": "RESULT",
                "TIME_ELAPSED": state['TIME_ELAPSED'] + elapsed,
                "WIN": True,
            })
        # Pause the game
        # Get the elapsed time and add to it. Reset Start_time when unpause
        elif inp_key_code in (ord("P"), ord("p")):
            elapsed = time.time() - state["START_TIME"]
            state.update({
                "SCREEN": "PAUSE",
                "TIME_ELAPSED": state['TIME_ELAPSED'] + elapsed,
            })

        # Open map
        # Reduce map couner by 1
        elif inp_key_code in (ord("M"), ord("m")) and state["MAP_COUNTER"] >= 0:
            state.update({
                "SCREEN": "MAP",
                "MAP_COUNTER": state["MAP_COUNTER"] - 1,
            })
        return state

    def __screen_pause(self, state, inp_key_code):
        if inp_key_code in (ord("C"), ord("c")):
            state.update({
                "SCREEN": "PLAY",
                "START_TIME": time.time(),
            })
        elif inp_key_code in (ord("S"), ord("s")):
            state.update({
                "SCREEN": "RESULT",
            })
        return state

    def __screen_result(self, state, inp_key_code):
        if inp_key_code in (ord("C"), ord("c")):
            state.update({
                "START_TIME": None,
                "TIME_ELAPSED": 0,  # in second
                "DIFFICULTY": None,  # easy or hard
                "SCREEN": "MENU",  # Which screen the user is at
                "MAP_COUNTER": 0,
                "WIN": False,
            })
        return state

    def __screen_map(self, state, inp_key_code):
        if inp_key_code in (ord("C"), ord("c")):
            state.update({
                "SCREEN": "PLAY",
            })
        return state

    # A dummy converter so the machine does not halt
    def __screen_default(self, state, inp):
        return state

    def get_next_values(self, state, inp_key_code):
        return {
            "MENU": self.__screen_menu,
            "WAIT": self.__screen_wait,
            "MAP": self.__screen_map,
            "PLAY": self.__screen_play,
            "PAUSE": self.__screen_pause,
            "RESULT": self.__screen_result,
        }.get(state["SCREEN"], self.__screen_default)(state, inp_key_code), None


class MazeRunner():
    def __init__(self, sm):
        self.sm = sm
        sm.start()
        self.mGPU = GPU()

    def start_screen(self):
        # set up the event handler function
        def input_event_handler(event):
            """
            Default unhandled event handler for handling simple scene navigation.
            """
            if isinstance(event, KeyboardEvent):
                c = event.key_code
                self.sm.step(c)
                if c in (ord("E"), ord("e"), ord("H"), ord("h"), ord("Q"), ord("q")):
                    raise StopApplication("Screen stopped by user")

        effects = [
            Print(self.mGPU.screen, FigletText("MAZE  RUNNER", font='big'),
                  y=self.mGPU.height//2 - 12),
            Print(self.mGPU.screen,
                  Fire(10, self.mGPU.width, "*" * self.mGPU.width, 1, 30, self.mGPU.screen.colours,
                       False),
                  y=self.mGPU.height - 5,
                  speed=1,
                  transparent=True),
            Print(self.mGPU.screen,
                  StaticRenderer(images=[r"Press [E] for EASY mode or [H] for HARD mode."]), y=self.mGPU.height//2 - 3 - 1),
            Print(self.mGPU.screen,
                  StaticRenderer(images=[r"Press [Q] to quit."]), y=self.mGPU.height//2 - 3),
            Print(self.mGPU.screen,
                  StaticRenderer(images=[r"""
         ▀▀▀██████▄▄▄
      ▄▄▄▄▄  █████████▄
     ▀▀▀▀█████▌ ▀▐▄ ▀▐█
   ▀▀█████▄▄ ▀██████▄██
   ▀▄▄▄▄▄  ▀▀█▄▀█════█▀
        ▀▀▀▄  ▀▀███ ▀      ▄▄
     ▄███▀▀██▄████████▄ ▄▀▀▀██▌
   ██▀▄▄▄██▀▄███▀ ▀▀████     ▀█▄
▄▀▀▀▄██▄▀▀▌████▒▒▒▒▒▒███    ▌▄▄▀
▌    ▐▀████▐███▒▒▒▒▒▐██▌
▀▄  ▄▀   ▀▀████▒▒▒▒▄██▀
  ▀▀      ▀▀█████████▀
        ▄▄██▀██████▀█
      ▄██▀     ▀▀▀  █
     ▄█             ▐▌
 ▄▄▄▄█▌              ▀█▄▄▄▄▀▀▄
▌     ▐                ▀▀▄▄▄▀
▀▀▀▀▀▀▀
    """]), y=self.mGPU.height//2)
            #                 Print(screen,
            #                       StaticRenderer(images=[r"""
            #       ${3,1}*
            #      / \
            #     /${1}o${2}  \
            #    /_   _\
            #     /   \${4}b
            #    /     \
            #   /   ${1}o${2}   \
            #  /__     __\
            #  ${1}d${2} / ${4}o${2}   \
            #   /       \
            #  / ${4}o     ${1}o${2}.\
            # /___________\
            #      ${3}|||
            #      ${3}|||
            #     """]), y=self.mGPU.height//2 + 3)
        ]

        self.mGPU.set_title("Maze Runner")
        self.mGPU.playScene(effects, stop_on_resize=True,
                            input_handler=input_event_handler)

    def wait_screen(self):

        def input_event_handler(event):
            if isinstance(event, KeyboardEvent):
                c = event.key_code
                self.sm.step(c)
                if c is ord(" "):
                    raise StopApplication("Screen stopped by user")

        # self.mGPU.setCurrentScreen(screen)
        effects = [
            Print(self.mGPU.screen, FigletText("DIFFICULTY:   {}".format(self.sm.state["DIFFICULTY"]), font='small'),
                  y=self.mGPU.height//2-10),
            Print(self.mGPU.screen,
                  Fire(10, self.mGPU.width, "*" * self.mGPU.width, 1, 30, self.mGPU.screen.colours,
                       False),
                  y=self.mGPU.height - 5,
                  speed=1,
                  transparent=True),
            Print(self.mGPU.screen, StaticRenderer(images=[r"""
_______________________________________________________________________________________
| OBJECTIVE                                                                            |
|--------------------------------------------------------------------------------------|
|                                                                                      |
|  You need to escape the maze ASAP. Find the ${1}RED${7} door!                                |
|  You are only allowed to look at the map for a limited number of times.              |
|                                                                                      |
|                                                                                      |
|  control : Press A, W, S, D to move around. Press Q and E to pan.                    |
|  Press M to look at the map (Psst you only can look at the map limited no. of time)  |
|  Press P to pause the game. (It can be tiring so take your time to solve the maze)   |
|                                                                                      |
|  Are you ready?  \☺/                                                                 |
|  Good luck!       []                                                                 |
|                   /\                        ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄      |
|                                             █        ▀█▄▀▄▀██████ ▀█▄▀▄▀██████       |
|  Press [SPACE BAR] to start the game                   ▀█▄█▄███▀    ▀█▄█▄███         |
|______________________________________________________________________________________|
            """]), y=self.mGPU.height//2 - 5)

        ]

        self.mGPU.set_title("Maze Runner")
        self.mGPU.playScene(effects, stop_on_resize=True,
                            input_handler=input_event_handler)

    def mapGenerator(self, difficulty) -> tuple:
        if difficulty == "HARD":
            masterMap = [
                "#########################################",
                "#s#...#.....#.....#...#...#.......#.#...#",
                "#.###.#.#.#.#.#####.#.#.###.#.#.#.#.#.###",
                "#.#...#.#.#...#...#.#.....#.#.#.#.....#.#",
                "#.#.#.#######.#.#######.#######.#####.#.#",
                "#...#.............#.#.....#.....#...#...#",
                "#.#####.###.###.#.#.###.#.#.#####.###.###",
                "#.....#.#.#.#...#...#.#.#.....#.#.#.....#",
                "###.#####.#.#####.###.###.#.###.#.#.#####",
                "#.......#.#...#.....#.....#.#.#...#.#...#",
                "#.#.#.###.#.#.#####.###.#.#.#.#.#####.###",
                "#.#.#.#.....#.#.........#.#.....#.#.....#",
                "#.###.#.#.#########.e##.#######.#.#####.#",
                "#.#...#.#.#...#.#.....#...#.#.#.#...#.#.#",
                "#.###.#######.#.###.#.#####.#.#.###.#.#.#",
                "#...#.........#.#...#.#.#.....#.......#.#",
                "#####.#.###.###.###.###.#.#.#.#.#.#.#.#.#",
                "#.....#.#...#.....#...#...#.#...#.#.#...#",
                "#.#.#.#.###.#.###.###.###.#.###.###.###.#",
                "#.#.#.#...#...#...#...#...#...#...#...#.#",
                "#########################################",
            ]
        else:
            masterMap = [
                "############",
                "#...#......#",
                "#s#.#.####.#",
                "###.#....#.#",
                "#....###.#.#",
                "####.#.#.#.#",
                "#..#.#.#.#.#",
                "##.#.#.#.#.#",
                "#........#.#",
                "######.###.#",
                "#......#...#",
                "########e###", ]
        startCoor = (0, 0)
        for y in range(len(masterMap)):
            if masterMap[y].find('s') != -1:
                startCoor = Coordinate(masterMap[y].find('s'), y)

        return masterMap, startCoor

    def result_screen(self):

        def even_handler(event):
            if isinstance(event, KeyboardEvent):
                c = event.key_code
                self.sm.step(c)
                if c in (ord("C"), ord("c")):
                    raise StopApplication("asd")

        if self.sm.state["WIN"]:
            title = "WON"
            art = r"""
                      █████████
  ███████          ███▒▒▒▒▒▒▒▒███
  █▒▒▒▒▒▒█       ███▒▒▒▒▒▒▒▒▒▒▒▒▒███
   █▒▒▒▒▒▒█    ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
    █▒▒▒▒▒█   ██▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒███
     █▒▒▒█   █▒▒▒▒▒▒████▒▒▒▒████▒▒▒▒▒▒██
   █████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
   █▒▒good job▒▒█▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒██
 ██▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒██▒▒▒▒▒▒▒▒▒▒██▒▒▒▒██
██▒▒▒███████████▒▒▒▒▒██▒▒▒▒▒▒▒▒██▒▒▒▒▒██
█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒████████▒▒▒▒▒▒▒██
██▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
 █▒▒▒███████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
 ██▒▒▒▒▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█
  ████████████  ░█████████████████
            """
        else:
            title = "FAILED"
            art = r"""
    ▄▄▄
  ▄▀░▄░▀▄
  █░█▄▀░█
  █░▀▄▄▀█▄█▄▀
█▄▄█▄▄▄▄███▀
a loser snail
            """

        effects = [
            Print(self.mGPU.screen, FigletText("YOU {}!".format(title), font='small'),
                  y=self.mGPU.height//2-10),
            Print(self.mGPU.screen, StaticRenderer(
                images=[r"Time taken is {:.3f} seconds".format(self.sm.state["TIME_ELAPSED"])]), y=self.mGPU.height//2 - 2 - 3),
            Print(self.mGPU.screen, StaticRenderer(
                images=[r"""Thank you for playing Maze Runner!"""]), y=self.mGPU.height//2 - 2 - 1),
            Print(self.mGPU.screen, StaticRenderer(images=[
                r"""Press [C] to continue."""]), y=self.mGPU.height//2 - 2+7),
            Print(self.mGPU.screen, StaticRenderer(
                images=[art]), y=self.mGPU.height//2 - 2+9)
        ]

        self.mGPU.set_title(title)
        self.mGPU.playScene(effects, stop_on_resize=True,
                            input_handler=even_handler)

    def pause_popup(self):
        title = "PAUSED"

        alive = True
        while alive:
            if self.sm.state["SCREEN"] in ("MENU", "QUIT"):
                return False  # True means that the game stops
            # Check input
            event = self.mGPU.get_event()
            if event and isinstance(event, KeyboardEvent):
                show_map = False
                c = event.key_code
                self.sm.step(c)
                if c in (ord("C"), ord("c")):
                    alive = False  # exit this loop and go back to main_game_loop
                elif c in (ord("S"), ord("s")):
                    self.result_screen()

            message = "The game is paused. Press [C] to continue. Press [S] to Stop game."
            self.mGPU.print_at(message, self.mGPU.width//2 -
                               len(message)//2, self.mGPU.height//2)

            message = "Time elapsed {:.3f} seconds.".format(
                self.sm.state["TIME_ELAPSED"])
            self.mGPU.print_at(message, self.mGPU.width//2 -
                               len(message)//2, self.mGPU.height//2 + 2)

            self.mGPU.set_title(title)
            self.mGPU.refresh()

        return True  # True means that the game continues

    def map_popup(self, player_pos, map):
        size_mapX = len(map[0])
        size_mapY = len(map)

        map_padding = ((self.mGPU.width - size_mapX)//2,  # left
                       (self.mGPU.height - size_mapY)//2,  # top
                       (self.mGPU.width + size_mapX)//2,  # right
                       (self.mGPU.height + size_mapY)//2,  # bottom
                       )

        alive = True
        for y in range(len(map)):
            map[y] = map[y].replace('s', '.')

        while alive:

            # Check input
            event = self.mGPU.get_event()
            if event and isinstance(event, KeyboardEvent):
                show_map = False
                c = event.key_code
                self.sm.step(c)
                if c in (ord("C"), ord("c")):
                    alive = False  # exit this loop and go back to main_game_loop

            for x in range(self.mGPU.width):
                for y in range(self.mGPU.height):
                    if (x - map_padding[0]) >= 0 and (x - map_padding[2]) < 0 and (y - map_padding[1]) >= 0 and (y - map_padding[3]) < 0:
                        if map[y - map_padding[1]][x - map_padding[0]] == 'e':
                            self.mGPU.print_at(map[y - map_padding[1]]
                                               [x - map_padding[0]], x, y, 1)
                        else:
                            self.mGPU.print_at(map[y - map_padding[1]]
                                               [x - map_padding[0]], x, y)

                    else:
                        self.mGPU.print_at(" ", x, y)

            self.mGPU.print_at(
                'O', map_padding[0]+player_pos.x_int, map_padding[1]+player_pos.y_int)

            message = "Left with {} map charge(s).".format(
                self.sm.state["MAP_COUNTER"])

            self.mGPU.print_at(
                message, (self.mGPU.width - len(message))//2, 5)

            message = "Press [C] to close map."
            self.mGPU.print_at(
                message, (self.mGPU.width - len(message))//2, self.mGPU.height - 5)

            self.mGPU.refresh()
        return False

    def main_screen(self):

        t1 = time.time()
        t2 = time.time()
        elapsedTime = 0.01

        # Preconfig
        mMap, player_pos = self.mapGenerator(
            self.sm.state["DIFFICULTY"])

        # player's position relative to the map
        player_pos = Coordinate(1.0, 1.0)
        player_vel = 2.0  # the velocity of the player per second
        player_arc = 0.0  # the angle to which the player is currently facing towards
        player_rotateVel = 3.14/1.5  # player's turn rate

        player_start_time = None
        player_end_time = None

        show_map = False

        FOV = math.pi / 3  # Field of view
        FOV_half = FOV/2
        FOV_delta_screen_width = FOV/self.mGPU.width
        focal_length = 1.5
        distance_too_far = 8
        distance_too_far_1 = distance_too_far * 0.55
        distance_too_far_2 = distance_too_far * 0.7

        screen_height_far = self.mGPU.height * 0.65
        screen_height_near = self.mGPU.height * 0.77

        alive = True

        door_found = False

        while alive:
            # Check input
            event = self.mGPU.get_event()
            if event and isinstance(event, KeyboardEvent):
                self.mGPU.print_at(
                    "Press [M] to look at the map ({} charge(s) left). Press [P] to pause the game.".format(self.sm.state["MAP_COUNTER"]), 0, 0)
                show_map = False
                c = event.key_code
                self.sm.step(c)
                if c in (ord("W"), ord("w")):
                    player_pos.translate(player_vel * elapsedTime, player_arc)
                    if (mMap[player_pos.y_int][player_pos.x_int] == "#"):
                        player_pos.translate(-1 * player_vel *
                                             elapsedTime, player_arc)
                elif c in (ord("S"), ord("s")):
                    player_pos.translate(-1 * player_vel *
                                         elapsedTime, player_arc)
                    if (mMap[player_pos.y_int][player_pos.x_int] == "#"):
                        player_pos.translate(player_vel *
                                             elapsedTime, player_arc)
                elif c in (ord("A"), ord("a")):
                    player_pos.translate(
                        player_vel * elapsedTime, player_arc - math.pi/2)
                    if (mMap[player_pos.y_int][player_pos.x_int] == "#"):
                        player_pos.translate(player_vel *
                                             elapsedTime, player_arc + math.pi/2)
                elif c in (ord("D"), ord("d")):
                    player_pos.translate(player_vel *
                                         elapsedTime, player_arc + math.pi/2)
                    if (mMap[player_pos.y_int][player_pos.x_int] == "#"):
                        player_pos.translate(player_vel *
                                             elapsedTime, player_arc - math.pi/2)
                elif c in (ord("Q"), ord("q")):  # Counter clockwise negative
                    player_arc -= player_rotateVel * elapsedTime
                elif c in (ord("E"), ord("e")):
                    player_arc += player_rotateVel * elapsedTime
                elif c in (ord("M"), ord("m")):
                    if self.sm.state["MAP_COUNTER"] >= 0:
                        self.map_popup(player_pos, mMap)
                    else:
                        self.mGPU.print_at(
                            "Map is no longer available. Good luck!                          ", 0, 0)
                elif c in (ord("P"), ord("p")):
                    if not self.pause_popup():
                        return
                elif c in (ord(" "), ord(" ")) and door_found:
                    self.sm.step("END")
                    if not self.result_screen():
                        alive = False
                        continue

            # Print 3D POV (Ray tracing)
            # Measure the distance from the player to the wall or other object. The further it is the smaller the object will look like
            # Measure distance by throwing a projectile untill it hits a wall (collison detection)
            for x in range(self.mGPU.width):
                distance = 0.0
                hit = False
                black_hit = False
                door_found = False
                golden_hit = False
                incr = 0.05
                # Shoot all rays towards the FOV then see what they hit
                while(not hit and distance < distance_too_far):
                    distance += incr
                    tar_x = player_pos.x + distance * \
                        math.cos(player_arc - FOV_half +
                                 x * FOV_delta_screen_width)
                    tar_y = player_pos.y + distance * \
                        math.sin(player_arc - FOV_half +
                                 x * FOV_delta_screen_width)

                    if '#' == mMap[int(tar_y)][int(tar_x)]:
                        hit = True
                        # if (tar_x - int(tar_x)) ** 2 + (tar_y - int(tar_y)) ** 2 <= 0.003 or (tar_x - int(tar_x+1)) ** 2 + (tar_y - int(tar_y+1)) ** 2 <= 0.003:
                        #     black_hit = True
                        # if (abs(tar_x - round(tar_x)) <= 0.05) and (abs(tar_y - round(tar_y)) <= 0.05):
                        #     black_hit = True

                        # Check if the ray touches the edges
                        # if the ray doesnt touch the center (90%) of the cell
                        if not((0.05 < tar_x % 1 < 0.95) or (0.05 < tar_y % 1 < 0.95)):
                            black_hit = True

                    elif 'e' == mMap[int(tar_y)][int(tar_x)]:
                        hit = True
                        golden_hit = True
                        if distance < 0.2:
                            door_found = True

                # Closest will have least ceiling and floor
                # Furthest will have most ceiling and floor
                # Linear mapping
                # TODO optimize this later
                # floorceil_thickness = (
                #     distance) * (diff_floorceil) / (distance_too_far) + min_floorceil
                floorceil_thickness = (
                    self.mGPU.height - focal_length * self.mGPU.height / (distance * 1.5))//2

                for y in range(1, self.mGPU.height):
                    # mini map

                    if floorceil_thickness < y < (self.mGPU.height - floorceil_thickness):
                        if black_hit:
                            self.mGPU.print_at(" ", x, y)
                        elif golden_hit and distance < distance_too_far_1:
                            self.mGPU.print_at("█", x, y, 1)
                        elif golden_hit and distance < distance_too_far_2:
                            self.mGPU.print_at("▒", x, y, 1)
                        elif golden_hit and distance < distance_too_far:
                            self.mGPU.print_at("░", x, y, 1)
                        elif distance < distance_too_far_1:
                            self.mGPU.print_at("█", x, y)
                        elif distance < distance_too_far_2:
                            self.mGPU.print_at("▒", x, y)
                        elif distance < distance_too_far:
                            self.mGPU.print_at("░", x, y)
                        else:
                            self.mGPU.print_at(" ", x, y)
                    elif (self.mGPU.height - floorceil_thickness) < y:
                        if y < screen_height_far:
                            self.mGPU.print_at('.', x, y)
                        elif y < screen_height_near:
                            self.mGPU.print_at("+", x, y)
                        else:
                            self.mGPU.print_at("#", x, y)
                    else:
                        self.mGPU.print_at(" ", x, y)

            # self.mGPU.set_title("Maze Runner: position: x:{:.3f}, y:{:.3f}, arc:{:.3f}, fps:{:.3f}".format(
            #     player_pos.x, player_pos.y, player_arc, 1/elapsedTime))

            t2 = time.time()
            elapsedTime = t2 - t1
            t1 = t2
            if door_found:
                self.mGPU.print_at('You have found the door!',
                                   self.mGPU.width//2-12, self.mGPU.height//2-1)
                self.mGPU.print_at('Hit [SPACE BAR] to escape!',
                                   self.mGPU.width//2-13, self.mGPU.height//2+1)
            self.mGPU.set_title(
                "Maze Runner [FPS:{:.3f}]".format(1/elapsedTime))
            self.mGPU.print_at('Time elapsed {:.3f} secs'.format(
                self.sm.state["TIME_ELAPSED"] + t2 - self.sm.state["START_TIME"]), 0, 1)
            self.mGPU.refresh()

    def end(self):
        self.mGPU.shutdown()
        sys.exit(0)

    def run(self):
        while True:
            try:
                if self.sm.state["SCREEN"] is "MENU":
                    self.start_screen()
                elif self.sm.state["SCREEN"] is "WAIT":
                    self.wait_screen()
                elif self.sm.state["SCREEN"] is "QUIT":
                    self.end()
                    print("Stopped gracefully.")
                    # print(self.sm.state)
                    sys.exit(0)
                else:
                    self.main_screen()

            except ResizeScreenError:
                pass


if __name__ == "__main__":
    mr = MazeRunner(StateMachine())
    mr.run()
