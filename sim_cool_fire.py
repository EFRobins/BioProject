# Dimensions: 2

# --- Set up executable path, do not edit ---

import sys
import inspect
import random

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
    config.title = "Probability_applied"
    config.dimensions = 2

    # State 0: chaparral
    # State 1: lake water
    # State 2: dense forest
    # State 3: scrubland in canyon
    # State 4: state of burning/keep burning/birth/survival/color of fire
    # State 5: state of death / stop burning
    # State 6: yellowy orange 1st stage burning
    # Stage 7: orange

    config.states = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    config.wrap = False
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.7, 0.7, 0.2), (0.4, 0.8, 1), (0.3, 0.4, 0),
                           (0.9, 1, 0), (0.7, 0, 0.1), (0.4, 0.4, 0.4), (1, 0.9, 0.2 ), (1, 0.6, 0.1), (0, 0, 0)]

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

    #setting forest
    gridray[25: 75, 60: 100] = 2
    gridray[80:140, 0:100] = 2

    # create the part of scrubland in canyon
    gridray[20:140, 120:140] = 3

    # create the part of lake :
    gridray[70:80, 20:100] = 1

    # create the part of town :
    gridray[175:185, 75:85] = 8

    # initial the condition: start firing on power plant here:


    for y in range(0, 1):
        for x in range(194, 200):
            gridray[y][x] = 6

    for i in range(0, 50):
        x = random.randint(0, 10)
        y = random.randint(0, 10)
        gridray[y][x] = 6

    config.set_initial_grid(gridray)

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


timeTrack = np.zeros((200, 200))
t = 0

def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # YOUR CODE HERE

    updateBurn(grid, neighbourstates, neighbourcounts,t)

    return grid


# the function of firing chaparall simulation:

def generateProbability(grid, northBurning, burningNeighbourCount):
    probability_0 = np.where(grid == 0, 0.1*burningNeighbourCount, 0)
    probability_2 = np.where(grid == 2, 0.02*burningNeighbourCount, 0)
    probability_3 = np.where(grid == 3, 0.4*burningNeighbourCount, 0)
    probability_all = probability_0 + probability_2 + probability_3
    probability_all_NW = np.where(northBurning, probability_all*1.2, probability_all)

    return probability_all_NW



def updateBurn(grid, neighbourstates, neighbourcounts,t ):

    # unpack the state arrays
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    # array of pixels with a northern pixel that is burning
    northBurning = (N == 6) | (NW == 6) | (NE == 6)

    randomNumber = np.random.rand(200, 200)
    toBurn = generateProbability(grid, northBurning, neighbourcounts[6]) > randomNumber

    burning = (grid == 6) | (grid == 4) | (grid == 7)

    itemindex = np.where(burning == True)
    timeTrack[itemindex] += 1
    toOrange = ((timeTrack == 30) & (gridray == 2)) | ((timeTrack == 1) & (gridray == 3)) | (
                (timeTrack == 10) & (gridray == 0)) | ((timeTrack == 10) & (gridray == 6))
    toRed = ((timeTrack == 70) & (gridray == 2)) | ((timeTrack == 3) & (gridray == 3)) | (
                (timeTrack == 20) & (gridray == 0)) | ((timeTrack == 20) & (gridray == 6))
    stopBurn = ((timeTrack >= 150) & (gridray == 2)) | ((timeTrack >= 8) & (gridray == 3)) | (
                (timeTrack >= 40) & (gridray == 0)) | ((timeTrack >= 40) & (gridray == 6))

    grid[toBurn] = 6
    grid[toOrange] = 7
    grid[toRed] = 4 
    grid[stopBurn] = 5

    t += 1
    printTime(grid, neighbourcounts)


def printTime(grid, neighbourCount):
    if ((grid == 8) & (neighbourCount[6] >= 1)).any():
        print("The fire reached the town at: ", str(t))


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


