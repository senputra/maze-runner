from asciimatics.effects import Print
from asciimatics.renderers import BarChart, FigletText, Fire, StaticRenderer
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import NextScene, ResizeScreenError, StopApplication
import sys
import math
import time
from random import randint
from asciimatics.event import KeyboardEvent

from libdw import sm
from time import sleep

dev_info = "init"


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
        "END_TIME": None,
        "TIME_ELAPSED": 0,  # in second
        "DIFFICULTY": None,  # easy or hard
        "SCREEN": "MENU",  # Which screen the user is at
        "MAP_COUNTER": 0,
        "WIN": False,
    }

    def screen_menu(self, state, inp_key_code):
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
                "DIFFICULTY": "EASY",
                "SCREEN": "QUIT",
                "MAP_COUNTER": 100,
            })

        return state

    def screen_wait(self, state, inp_key_code):
        if inp_key_code in (ord(" "), ord("\n")):
            state.update({
                "SCREEN": "PLAY",
                "START_TIME": time.time(),
            })
        return state

    def screen_play(self, state, inp_key_code):
        # Pause the game
        # Get the elapsed time and add to it. Reset Start_time when unpause
        if inp_key_code in (ord("P"), ord("p")):
            elapsed = time.time() - state["START_TIME"]
            state.update({
                "SCREEN": "PAUSE",
                "TIME_ELAPSED": state['TIME_ELAPSED'] + elapsed,
            })

        # Open map
        # Reduce map couner by 1
        if inp_key_code in (ord("M"), ord("m")) and state["MAP_COUNTER"] >= 0:
            state.update({
                "SCREEN": "MAP",
                "MAP_COUNTER": state["MAP_COUNTER"] - 1,
            })
        return state

    def screen_pause(self, state, inp_key_code):
        if inp_key_code in (ord("C"), ord("c")):
            state.update({
                "SCREEN": "PLAY",
                "START_TIME": time.time(),
            })
        elif inp_key_code in (ord("Q"), ord("q")):
            state.update({
                "SCREEN": "RESULT",
            })
        return state

    def screen_result(self, state, inp_key_code):
        if inp_key_code in (ord("R"), ord("r")):
            state.update({
                "START_TIME": None,
                "END_TIME": None,
                "TIME_ELAPSED": 0,  # in second
                "DIFFICULTY": None,  # easy or hard
                "SCREEN": "MENU",  # Which screen the user is at
                "MAP_COUNTER": 0,
                "WIN": False,
            })
        elif inp_key_code in (ord("Q"), ord("q")):
            state.update({
                "SCREEN": "QUIT",
            })
        return state

    def screen_map(self, state, inp_key_code):
        if inp_key_code in (ord("C"), ord("c")):
            state.update({
                "SCREEN": "PLAY",
            })
        return state

    def get_next_values(self, state, inp_key_code):
        return {
            "MENU": self.screen_menu,
            "WAIT": self.screen_wait,
            "MAP": self.screen_map,
            "PLAY": self.screen_play,
            "PAUSE": self.screen_pause,
            "RESULT": self.screen_result,
        }.get(state["SCREEN"], state)(state, inp_key_code), None


class MazeRunner():
    def __init__(self, sm):
        self.sm = sm
        sm.start()

    def screenSizeCheck(self, screen, size_x=120, size_y=30) -> bool:
        scenes = []

        # if screen.width != size_x or screen.height != size_y:
        #     effects = [
        #         Print(screen, FigletText("Resize to {}x{}".format(size_x, size_y)),
        #               y=screen.height//2-6),
        #         Print(screen, FigletText("now is {}x{}".format(screen.width, screen.height)),
        #               y=screen.height//2+3),
        #     ]
        #     scenes.append(Scene(effects, -1))
        #     screen.play(scenes, stop_on_resize=True)
        #     return False
        return True

    def start_screen_event_handler(self, event):
        """
        Default unhandled event handler for handling simple scene navigation.
        """
        if isinstance(event, KeyboardEvent):
            c = event.key_code
            self.sm.step(c)
            if c in (ord("E"), ord("e"), ord("H"), ord("h"), ord("Q"), ord("q")):
                raise StopApplication("Screen stopped by user")

    def start_screen(self, screen):
        global dev_info

        scenes = []
        if self.screenSizeCheck(screen):
            effects = [
                Print(screen, FigletText("MAZE  RUNNER", font='big'),
                      y=screen.height//2 - 12),
                Print(screen,
                      Fire(10, screen.width, "*" * screen.width, 1, 30, screen.colours,
                           False),
                      y=screen.height - 6,
                      speed=1,
                      transparent=True),
                Print(screen,
                      StaticRenderer(images=[r"Press [E] for EASY mode or [H] for HARD mode."]), y=screen.height//2 - 3 - 1),
                Print(screen,
                      StaticRenderer(images=[r"Press [Q] to quit."]), y=screen.height//2 - 3),
                Print(screen,
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
    """]), y=screen.height//2)
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
                #     """]), y=screen.height//2 + 3)
            ]

            screen.set_title("Maze Runner")
            scenes.append(Scene(effects, -1))
            screen.play(scenes, stop_on_resize=True,
                        unhandled_input=self.start_screen_event_handler)

    def wait_screen_event_handler(self, event):
        if isinstance(event, KeyboardEvent):
            c = event.key_code
            self.sm.step(c)
            if c is ord(" "):
                raise StopApplication("Screen stopped by user")

    def wait_screen(self, screen):
        scenes = []
        if self.screenSizeCheck(screen):
            effects = [
                Print(screen, FigletText("DIFFICULTY:   {}".format(self.sm.state["DIFFICULTY"]), font='small'),
                      y=screen.height//2-10),
                Print(screen,
                      Fire(10, screen.width, "*" * screen.width, 1, 30, screen.colours,
                           False),
                      y=screen.height - 5,
                      speed=1,
                      transparent=True),
                Print(screen, StaticRenderer(images=[r"""
_____________________________________________________________________________________
| OBJECTIVE                                                                          |
|------------------------------------------------------------------------------------|
|                                                                                    |
|  You need to escape the maze ASAP. Find the GOLDEN door                            |
|  You are only allowed to look at the map 3 times.                                  |
|                                                                                    |
|                                                                                    |
|  control : Press A, W, S, D to move around. Press Q and E to pan.                  |
|                                                                                    |
|  Press P to pause the game. (It can be tiring so take your time to solve the maze) |
|                                                                                    |
|  Are you ready?  \☺/                                                               |
|  Good luck!       []                                                               |
|                   /\                        ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄    |
|                                             █        ▀█▄▀▄▀██████ ▀█▄▀▄▀██████     |
|  Press [SPACE BAR] to start the game                   ▀█▄█▄███▀    ▀█▄█▄███       |
|____________________________________________________________________________________|
                """]), y=screen.height//2 - 5)

            ]

            screen.set_title("Maze Runner")
            scenes.append(Scene(effects, -1))
            screen.play(scenes, stop_on_resize=True,
                        unhandled_input=self.wait_screen_event_handler)

    def mapGenerator(self, difficulty) -> list:
        if difficulty == "HARD":
            return [
                "################",
                "#.......#......#",
                "#.......#...####",
                "######..#......#",
                "#.......###....#",
                "#...#####...####",
                "#.......##.....#",
                "######..##.....#",
                "#.......##.....#",
                "#.......##.#####",
                "#.....#.##.....#",
                "#.....#.##.....#",
                "#.....#........#",
                "#.....#..#.....#",
                "#........#.....#",
                "################", ]
        else:
            return [
                "################",
                "#.......#......#",
                "#.......#...####",
                "##......#......#",
                "#.......#.#....#",
                "#.......#.######",
                "#.......#......#",
                "##......#......#",
                "#.......#......#",
                "#...#####..#####",
                "#.......#......#",
                "#.......#......#",
                "#..............#",
                "#........#.....#",
                "#........#.....#",
                "################", ]

    def result_screen(self, screen):

        def even_handler(event):
            if isinstance(event, KeyboardEvent):
                c = event.key_code
                self.sm.step(c)
                if c in (ord("R"), ord("r")):
                    raise StopApplication("asd")
                elif c in (ord("Q"), ord("q")):
                    raise StopApplication("asd")
        if self.sm.state["WIN"] is not False:
            title = "FAILED"
            art = r"""
    ▄▄▄
  ▄▀░▄░▀▄
  █░█▄▀░█
  █░▀▄▄▀█▄█▄▀
█▄▄█▄▄▄▄███▀
a loser snail
            """
        else:
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

        scenes = []
        if self.screenSizeCheck(screen):
            effects = [
                Print(screen, FigletText("YOU {}!".format(title), font='small'),
                      y=screen.height//2-10),
                Print(screen, StaticRenderer(
                    images=[r"Time taken is {:.3f} seconds".format(self.sm.state["TIME_ELAPSED"])]), y=screen.height//2 - 2 - 3),
                Print(screen, StaticRenderer(
                    images=[r"""Thank you for playing Maze Runner!"""]), y=screen.height//2 - 2 - 1),
                Print(screen, StaticRenderer(images=[
                      r"""Press [R] to restart the game and [Q] to quit."""]), y=screen.height//2 - 2+7),
                Print(screen, StaticRenderer(
                    images=[art]), y=screen.height//2 - 2+9)
            ]

            screen.set_title("Maze Runner")
            scenes.append(Scene(effects, -1))
            screen.play(scenes, stop_on_resize=True,
                        unhandled_input=even_handler)

    def pause_screen(self, screen):
        title = "PAUSED"

        alive = True
        while alive:
            if self.sm.state["SCREEN"] in ("MENU", "QUIT"):
                return False  # True means that the game stops
            # Check input
            event = screen.get_event()
            if event and isinstance(event, KeyboardEvent):
                show_map = False
                c = event.key_code
                self.sm.step(c)
                if c in (ord("C"), ord("c")):
                    alive = False  # exit this loop and go back to main_game_loop
                elif c in (ord("Q"), ord("q")):
                    self.result_screen(screen)

            message = "The game is paused. Press [C] to continue. Press [Q] to Quit."
            screen.print_at(message, screen.width//2 -
                            len(message)//2, screen.height//2)

            message = "Time elapsed {:.3f} seconds.".format(
                self.sm.state["TIME_ELAPSED"])
            screen.print_at(message, screen.width//2 -
                            len(message)//2, screen.height//2 + 2)

            screen.set_title(title)
            screen.refresh()

        return True  # True means that the game continues

    def map_screen(self, screen, map_padding, player_pos, mMap):
        alive = True
        while alive:

            # Check input
            event = screen.get_event()
            if event and isinstance(event, KeyboardEvent):
                show_map = False
                c = event.key_code
                self.sm.step(c)
                if c in (ord("C"), ord("c")):
                    alive = False  # exit this loop and go back to main_game_loop

            for x in range(screen.width):
                for y in range(screen.height):
                    if (x - map_padding[0]) >= 0 and (x - map_padding[2]) < 0 and (y - map_padding[1]) >= 0 and (y - map_padding[3]) < 0:
                        screen.print_at(mMap[y - map_padding[1]]
                                        [x - map_padding[0]], x, y)
                    else:
                        screen.print_at(" ", x, y)

            screen.print_at(
                'O', map_padding[0]+player_pos.x_int, map_padding[1]+player_pos.y_int)

            message = "Left with {} map charges".format(
                self.sm.state["MAP_COUNTER"])

            screen.print_at(
                message, (screen.width - len(message))//2, 5)

            message = "Press [C] to close map."
            screen.print_at(
                message, (screen.width - len(message))//2, screen.height - 5)

            screen.refresh()
        return False

    def main_game_loop(self, screen, mMap=None):
        t1 = time.time()
        t2 = time.time()
        elapsedTime = 0.01

        # Preconfig
        mMap = self.mapGenerator(self.sm.state["DIFFICULTY"])

        size_mapX = len(mMap[0])
        size_mapY = len(mMap)

        map_padding = ((screen.width - size_mapX)//2,  # left
                       (screen.height - size_mapY)//2,  # top
                       (screen.width + size_mapX)//2,  # right
                       (screen.height + size_mapY)//2,  # bottom
                       )

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
        FOV_delta_screen_width = FOV/screen.width

        distance_too_far = size_mapX // 3
        distance_too_far_1 = distance_too_far * 0.55
        distance_too_far_2 = distance_too_far * 0.7

        screen_height_far = screen.height * 0.55
        screen_height_near = screen.height * 0.7

        max_floorceil = screen.height // 2.01
        min_floorceil = screen.height // 20
        diff_floorceil = max_floorceil - min_floorceil

        alive = True

        while alive:
            if not self.screenSizeCheck(screen):
                continue
            # Check input
            event = screen.get_event()
            if event and isinstance(event, KeyboardEvent):
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
                        self.map_screen(screen, map_padding, player_pos, mMap)
                    else:
                        screen.print_at(
                            "Map is no longer available. Good luck!", 0, 0)
                elif c in (ord("P"), ord("p")):
                    alive = self.pause_screen(screen)

            # Print 3D POV (Ray tracing)
            # Measure the distance from the player to the wall or other object. The further it is the smaller the object will look like
            # Measure distance by throwing a projectile untill it hits a wall (collison detection)
            for x in range(screen.width):
                distance = 0.0
                hit = False
                black_hit = False
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

                # Closest will have least ceiling and floor ( 1/10 each )
                # Furthest will have most ceiling and floor ( 1/3 each)

                # TODO optimize this later
                floorceil_thickness = (
                    distance) * (diff_floorceil) / (distance_too_far) + min_floorceil

                for y in range(1, screen.height):
                    # mini map

                    if floorceil_thickness < y < (screen.height - floorceil_thickness):
                        if black_hit:
                            screen.print_at(" ", x, y)
                        elif distance < distance_too_far_1:
                            screen.print_at("█", x, y)
                        elif distance < distance_too_far_2:
                            screen.print_at("▒", x, y)
                        elif distance < distance_too_far:
                            screen.print_at("░", x, y)
                        else:
                            screen.print_at(" ", x, y)
                    elif (screen.height - floorceil_thickness) < y:
                        if y < screen_height_far:
                            screen.print_at('.', x, y)
                        elif y < screen_height_near:
                            screen.print_at("+", x, y)
                        else:
                            screen.print_at("#", x, y)
                    else:
                        screen.print_at(" ", x, y)

            # screen.set_title("Maze Runner: position: x:{:.3f}, y:{:.3f}, arc:{:.3f}, fps:{:.3f}".format(
            #     player_pos.x, player_pos.y, player_arc, 1/elapsedTime))
            screen.set_title("Maze Runner [FPS:{:.3f}]".format(1/elapsedTime))
            # screen.print_at('p', player_pos.x_int, player_pos.y_int)
            screen.refresh()

            t2 = time.time()
            elapsedTime = t2 - t1
            t1 = t2

    def main_screen(self, screen):
        self.main_game_loop(screen)

    def run(self):
        while True:
            try:
                if self.sm.state["SCREEN"] is "MENU":
                    Screen.wrapper(self.start_screen)
                elif self.sm.state["SCREEN"] is "WAIT":
                    Screen.wrapper(self.wait_screen)
                elif self.sm.state["SCREEN"] is "QUIT":
                    print("Stopped gracefully")
                    print(self.sm.state)
                    sys.exit(0)
                else:
                    Screen.wrapper(self.main_screen)

            except ResizeScreenError:
                pass
            # Screen.wrapper(demo)


if __name__ == "__main__":
    mr = MazeRunner(StateMachine())
    mr.run()
