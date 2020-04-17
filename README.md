# Maze Runner [DW Final Assignment]

## Introduction

**Maze Runner** is a First Person Shooting game that is run on a terminal window. TH

Dependencies:

1. libdw

2. asciimatics - Install by running `conda install -c conda-forge asciimatics`.

## How to play

1. Ensure that asciimatics and libdw are installed

2. Open power shell (Ctrl X + A)

   ```bash
   # Change the power shell to the project directory
   $ cd </project/folder>
   # run the game
   $ python ./main.py
   ```

## Documentation

### _class_ GPU()

`GPU` is a wrapper for `asciimatic` library.`GPU` allows other classes to **print** any ASCII character on the terminal window and to **get** the keyboard and mouse input event from the terminal window.

**Properties:**

- **screen** - get the Screen object of the terminal window.
- **height** - The number of lines in the window.
- **width** - The number of character in one line.

**Constants:**

- **\_\_DISABLE_KEYBOARD_INTERRUPT** - Disable keyboard interruption in terminal. For example, ignoring `^Z` or `^C`.

#### start()

> ​Grab the lower lever control of the terminal window it is on.

#### shutdown( _restore=True_ )

> Close the current screen and clear buffer to prevent memory leaks.

**Parameters:**

- **restore** – If True, only discard the display buffer of the terminal window. Otherwise, remove buffer and closes all the opened input to the terminal window

#### print_at( *char: str, x: int, y: int, color=7, attr=0, bg=0, transparent=False* )

> Print the text at the specified location using the specified colour and attributes.

**Parameters:**

- **char** – The (single line) text to be printed.
- **x** – The column (x coord) for the start of the text.
- **y** – The line (y coord) for the start of the text.
- **colour** – The colour of the text to be displayed.
- **attr** – The cell attribute of the text to be displayed.
- **bg** – The background colour of the text to be displayed.
- **transparent** – Whether to print spaces or not, thus giving a transparent effect.

**Returns:** None

The colours and attributes are as follow. Note that not all terminal supports the colour and attributes.

```python
COLOUR_RED = 1
COLOUR_GREEN = 2
COLOUR_YELLOW = 3
COLOUR_BLUE = 4
COLOUR_MAGENTA = 5
COLOUR_CYAN = 6
COLOUR_WHITE = 7

A_BOLD = 1
A_NORMAL = 2
```

#### def get_event()

Check for any events (e.g. key-press or mouse movement) without waiting.

**Returns:** A Event object if anything was detected, otherwise it returns None.

#### refresh()

> Flush the buffer to the terminal window

**Returns:** None

#### set_title( *title:str* )

> Set the title for this terminal window. This will typically change the text displayed in the window title bar.

**Parameters:**

- **title** – The title to be set.

**Returns:** None

#### playScene( _effect_list: list, duration=-1, stop_on_resize=True, input_handler=None_ )

> Loop through the list of effect.

**Parameters:**

- **effect_list** – The list of preset effect to be playes
- **duration** – The amount of time the scene will play for. A value of –1 means don’t stop.
- **stop_on_resize** – Whether to stop when the screen is resized. Default is to carry on regardless – which will typically result in an error.
- **input_handler** – Function to call for any input.
  The input_handler input function just takes one parameter – the input event that was not handled.

---

### _class_ Coordinate( _x:float, y:float_ )

A point object in a `2D` space.

**Parameters:**

- **x** – The x coordinate.
- **y** – The y coordinate.

**Properties:**

- **x** – The x coordinate in float.
- **y** – The y coordinate in float.
- **x_int** – The x coordinate in integer.
- **y_int** – The y coordinate in integer.

#### translate( _distance:float, angle:float_ )

> Move the point towards a direction.

**Parameters:**

- **distance** – The magnitude of how far the point moves.
- **angle** – The direction where the point moves to

**Returns:** None

---

### _class_ MazeRunner()

#### main_screen()

> This is the main screen of the game. The concept of Ray Tracing is used to estimate the color of a every pixel rendered from the map.

#### mapGenerator( _difficulty:str_ )

> Generate maze depends on the difficulty set.

**Parameters:**

- **difficulty** – The set difficulty of the map. `EASY` for easy map and `HARD` for a more difficult map.

**Returns:** The maze in a list of string.

#### start_screen()

> Display the main menu for user to see when the game starts.

#### wait_screen()

> Display the rules and objectives of the map to the user.

#### result_screen()

> Display the result of the round to the user

#### pause_popup()

> Pop up a screen that pauses the game. Time is stopped also.

#### map_popup( *player_pos:Coordinate, map:list* )

> Pop up a screen that shows the map of the maze, the location of the player and the location of the objective. There is a limited amount of time the user can use the map.

#### run()

> Start the game.

#### end()

> Shutdown the GPU object and clear up all the used memory. Exit the game.

**Parameters:**

- **player_pos** – The coordinate object of the player.
- **map** – The map of the round.

**Returns:** None

---

### _class_ StateMachine

> The object that stores the machine state and is responsible for upper level state management.

**Properties:**

- **start_state** – The initial state of the machine.

#### get_next_values(state, inp_key_code)

> Process the input with the current state of the machine.

The extension function of get_next_values().

```python
__screen_menu(self, state, inp_key_code)
__screen_wait(self, state, inp_key_code)
__screen_play(self, state, inp_key_code)
__screen_pause(self, state, inp_key_code)
__screen_result(self, state, inp_key_code)
__screen_map(self, state, inp_key_code)
__screen_default(self, state, inp)
```

**Properties:**

- **state** – The current state of the machine.
- **inp_key_code** – The input key pressed on the keyboard.

**Returns:**

- **next_state** – The next state of the machine.
- **output** – The output from the input and the current state machine.

---

### State Machine

State

1. Before starting
2. Timer starts
3. Show maps (record how long the map is being used for)
4. Finish State

### Coding checkpoints

- [x] use asciimatics to try make a splash screen

```python
######################################################################
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                       PRESS ENTER TO START                         #
#                                                                    #
######################################################################
```

- [x] make level 1 map (Bird view)

- [x] use get_input() to move user from the level 1 map

- [x] make a 3d perspective

  - [x] Use ray collision detection. Further one less shady then the nearer one (see if can apply anti aliasing)
  - [x] option B:
    - [x] Use premade perspective ascii to make the map.

- [x] Testing
- [x] Optimize

## Brain Storming

## User Flow

1. click enter to start
2. start from level 1 - 10
3. there is a timer that starts counting
4. level 1 is to get used to the control
5. keyboard `A, W, S, and D` to move
6. mouse dragging to rotate camera.

### Future Improvements

1. Move to a more efficient programmin language. Currently it performs at 30 FPS in average.
2. Online leaderboard

## Focal length vs perspective

https://photo.stackexchange.com/questions/40981/what-is-the-relationship-between-size-of-object-with-distance

![image-20200412140041440](C:\Users\dodys\AppData\Roaming\Typora\typora-user-images\image-20200412140041440.png)
