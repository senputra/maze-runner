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


class FirstWordSM(sm.SM):
    start_state = {
        "title": "splash"
    }

    def get_next_values(self, state, inp):
        if state == 0:
            if inp != ' ' and inp != '\n':
                ns = 1
                o = inp
            else:
                ns = 0
                o = None
        elif state == 1:
            if inp == ' ':
                ns = 2
                o = None
            elif inp == '\n':
                ns = 0
                o = None
            else:
                ns = 1
                o = inp
        elif state == 2:
            if inp == '\n':
                ns = 0
                o = None
            else:
                ns = 2
                o = None
        return next_state, output


def screenSizeCheck(screen, size_x=120, size_y=30) -> bool:
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


def default_input_handler(event):
    """
       Default unhandled event handler for handling simple scene navigation.
    """
    if isinstance(event, KeyboardEvent):
        c = event.key_code
        if c in (ord("X"), ord("x"), ord("Q"), ord("q")):
            raise StopApplication("User terminated app")
        if c in (ord(" "), ord("\n"), ord("\r")):
            raise NextScene()


def start_screen_event_handler(event):
    """
       Default unhandled event handler for handling simple scene navigation.
    """
    if isinstance(event, KeyboardEvent):
        c = event.key_code
        if c in (ord("X"), ord("x"), ord("Q"), ord("q")):
            raise StopApplication("User terminated app")
        if c in (ord(" "), ord("\n"), ord("\r")):
            raise NextScene()


def start_screen(screen):
    global dev_info

    scenes = []
    if screenSizeCheck(screen):
        effects = [
            Print(screen,
                  StaticRenderer(images=["dev info: {}".format(dev_info)]), y=0, x=0),
            Print(screen, FigletText("Maze Runner", font='big'),
                  y=screen.height//2-6),
            Print(screen,
                  Fire(10, screen.width, "*" * screen.width, 1, 30, screen.colours,
                       False),
                  y=screen.height - 5,
                  speed=1,
                  transparent=True),
            Print(screen,
                  StaticRenderer(images=[r"Press ENTER"]), y=screen.height//2 + 3),
            Print(screen,
                  StaticRenderer(images=[r"""
      ${3,1}*
     / \
    /${1}o${2}  \
   /_   _\
    /   \${4}b
   /     \
  /   ${1}o${2}   \
 /__     __\
 ${1}d${2} / ${4}o${2}   \
  /       \
 / ${4}o     ${1}o${2}.\
/___________\
     ${3}|||
     ${3}|||
"""]), y=screen.height//2 + 3)
        ]

        screen.set_title("Maze Runner")
        scenes.append(Scene(effects, -1))
        screen.play(scenes, stop_on_resize=True,
                    unhandled_input=start_screen_event_handler)


def main_screen(screen, fps=60):
    # Preconfig
    mMap = [
        "################",
        "#..............#",
        "#..............#",
        "#..............#",
        "#.....####.....#",
        "#.....####.....#",
        "#.....####.....#",
        "#.....####.....#",
        "#..............#",
        "#..........#####",
        "#.....#........#",
        "#.....#........#",
        "#.....#........#",
        "#.....#........#",
        "#..............#",
        "################", ]

    size_mapX = len(mMap[0])
    size_mapY = len(mMap)

    map_padding = ((screen.width - size_mapX)//2,  # left
                   (screen.height - size_mapY)//2,  # top
                   (screen.width + size_mapX)//2,  # right
                   (screen.height + size_mapY)//2,  # bottom
                   )

    player_pos = Coordinate(1.0, 1.0)  # player's position relative to the map
    player_vel = 5.0  # the velocity of the player per second
    player_arc = 0.0  # the angle to which the player is currently facing towards
    player_rotateVel = 3.14  # player's turn rate
    frametime = 1.0/fps

    FOV = math.pi / 4  # Field of view

    distance_too_far = size_mapX // 2
    max_floorceil = screen.height // 2.1
    min_floorceil = screen.height // 20

    while True:
        if not screenSizeCheck(screen):
            continue
        # Check input
        event = screen.get_event()
        if event:
            if isinstance(event, KeyboardEvent):
                c = event.key_code
                if c in (ord("W"), ord("w")):
                    player_pos.translate(player_vel * frametime, player_arc)
                elif c in (ord("S"), ord("s")):
                    player_pos.translate(-1 * player_vel *
                                         frametime, player_arc)
                elif c in (ord("A"), ord("a")):  # Counter clockwise negative
                    player_arc -= player_rotateVel * frametime
                elif c in (ord("D"), ord("d")):
                    player_arc += player_rotateVel * frametime

        # Print map to the center of the screen
        # for x in range(screen.width):
        #     for y in range(screen.height):
        #         if (x - map_padding[0]) >= 0 and (x - map_padding[2]) < 0 and (y - map_padding[1]) >= 0 and (y - map_padding[3]) < 0:
        #             screen.print_at(mMap[y - map_padding[1]]
        #                             [x - map_padding[0]], x, y)
        #         else:
        #             screen.print_at(" ", x, y)

        # screen.refresh()

        # Print 3D POV
        # Measure the distance from the player to the wall or other object. The further it is the smaller the object will look like
        # Measure distance by throwing a projectile untill it hits a wall (collison detection)
        for x in range(screen.width):
            distance = 0.0
            hit = False
            black_hit = False
            incr = 0.05
            while(not hit and distance < distance_too_far):
                distance += incr
                tar_x = player_pos.x + distance * \
                    math.cos(player_arc - (FOV/2) + x * FOV/screen.width)
                tar_y = player_pos.y + distance * \
                    math.sin(player_arc - (FOV/2) + x * FOV/screen.width)

                if '#' == mMap[int(tar_y)][int(tar_x)]:
                    hit = True
                    if (tar_x - int(tar_x)) ** 2 + (tar_y - int(tar_y)) ** 2 <= 0.003:
                        black_hit = True

            # Closest will have least ceiling and floor ( 1/10 each )
            # Furthest will have most ceiling and floor ( 1/3 each)

            # TODO optimize this later
            floorceil_thickness = (distance - 0.05) * (max_floorceil -
                                                       min_floorceil) / (distance_too_far - 0.05) + min_floorceil

            for y in range(screen.height):
                # mini map
                if (x < size_mapX) and (y < (size_mapY+1)):
                    screen.print_at(mMap[y-1][x], x, y)
                else:
                    if floorceil_thickness < y < (screen.height - floorceil_thickness):
                        if black_hit:
                            screen.print_at(" ", x, y)
                        elif distance < distance_too_far * 0.1:
                            screen.print_at("█", x, y)
                        elif distance < distance_too_far * 0.6:
                            screen.print_at("▒", x, y)
                        elif distance < distance_too_far * 1:
                            screen.print_at("░", x, y)
                        else:
                            screen.print_at(" ", x, y)
                    elif (screen.height - floorceil_thickness) < y:
                        screen.print_at(".", x, y)
                    else:
                        screen.print_at(" ", x, y)

        screen.print_at("position: x:{}, y:{}, arc:{}".format(
            player_pos.x, player_pos.y, player_arc), 0, 0)
        screen.print_at('p', player_pos.x_int, player_pos.y_int + 1)
        screen.refresh()
        sleep(1/fps)


while True:
    try:
        Screen.wrapper(start_screen)
        Screen.wrapper(main_screen)
        print("Stopped gracefully")

        sys.exit(0)
    except ResizeScreenError:
        pass
    # Screen.wrapper(demo)
