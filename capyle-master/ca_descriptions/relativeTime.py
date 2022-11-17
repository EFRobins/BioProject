# Name: hongyu_simulation1
# Dimensions: 2

# --- Set up executable path, do not edit ---

import sys
import inspect

import numpy as np

this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "hongyu_simulation1"
    config.dimensions = 2

    # State 0: chaparral
    # State 1: lake water
    # State 2: dense forest
    # State 3: scrubland in canyon
    # State 4: state of burning/keep burning/birth/survival/color of fire
    # State 5: state of death / stop burning

    config.states = (0, 1, 2, 3, 4, 5)
    config.wrap = False
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.7, 0.7, 0.2), (0.4, 0.8, 1), (0.3, 0.4, 0),
                           (0.9, 1, 0), (0.7, 0, 0.1), (0.4, 0.4, 0.4)]

    config.num_generations = 1000
    # countNum = 0
    config.grid_dims = (200, 200)
    global gridray
    gridray = np.zeros((200, 200))
    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change


    # create the caparral:
    # for y in range(0, 200):
    #     for x in range(0, 200):
    #         gridray[y][x] = 0

    # create the part of dense forest:
    for y in range(25, 75):
        for x in range(60, 100):
            gridray[y][x] = 2

    for y in range(80, 140):
        for x in range(0, 100):
            gridray[y][x] = 2

    # create the part of scrubland in canyon
    for y in range(20, 140):
        for x in range(120, 140):
            gridray[y][x] = 3

    # create the part of lake :
    for y in range(70, 80):
        for x in range(20, 100):
            gridray[y][x] = 1

    # initial the condition: start firing on power plant here:

    for y in range(0, 3):
        for x in range(0, 10):
            gridray[y][x] = 4

    for y in range(0, 1):
        for x in range(194, 200):
            gridray[y][x] = 4


    config.set_initial_grid(gridray)

    if len(args) == 2:
        config.save()
        sys.exit()

    return config

timeTrack = np.zeros((200,200))
def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # YOUR CODE HERE

    burning = (grid == 4)
    
    updateBurn(grid, neighbourstates, neighbourcounts)

    return grid


# the function of firing chaparall simulation:

def updateBurn(grid, neighbourstates, neighbourcounts):

    # unpack the state arrays
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    #array of pixels with a northern pixel that is burning
    northBurning = (N == 4) | (NW == 4 ) | (NE == 4) | (SW == 3) | (SE == 3) | (W == 3) | (E == 3)
    
    #array of all possible burning arrays
    burnableCells =  (grid == 0 ) | (grid == 2 ) | (grid == 3 )
    burningNeighbours = (neighbourcounts[4] > 2)
    
    #set of cells to start burning
    toBurn = burnableCells & burningNeighbours & northBurning


    burning = (grid == 4)
    
    itemindex = np.where(burning == True)
    timeTrack[itemindex] += 1
    stopBurn = ((timeTrack >= 100) & (gridray == 2)) | ((timeTrack >= 5) & (gridray == 3)) | ((timeTrack >= 35) & (gridray == 0)) | ((timeTrack >= 35) & (gridray == 4))

    grid[toBurn] = 4
    grid[stopBurn] = 5

def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    grid = Grid2D(config, transition_function)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()
    
    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
