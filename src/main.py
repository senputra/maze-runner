from asciimatics.screen import Screen
from time import sleep


def demo(screen):

    # Config
    i = 0
    fps = 30

    # Constants
    COLOUR_BLACK = 0
    COLOUR_RED = 1
    COLOUR_GREEN = 2
    COLOUR_YELLOW = 3
    COLOUR_BLUE = 4
    COLOUR_MAGENTA = 5
    COLOUR_CYAN = 6
    COLOUR_WHITE = 7

    A_BOLD = 1
    A_NORMAL = 2
    A_REVERSE = 3
    A_UNDERLINE = 4

    while True:
        inp = screen.wait_for_input(1)
        screen.print_at(u'Call me! {}. Event {}'.format(i, inp),
                        0, 0, COLOUR_GREEN, A_BOLD)
        screen.refresh()
        i += 1
        sleep(1/fps)


Screen.wrapper(demo)
