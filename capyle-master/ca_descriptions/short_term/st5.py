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
                           (0.9, 1, 0), (0.7, 0, 0.1), (0.4, 0.4, 0.4), (1, 0.9, 0.2), (1, 0.6, 0.1), (0, 0, 0)]

    global geneNum
    config.num_generations = 1000
    geneNum = config.num_generations
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

    # setting forest
    gridray[25: 75, 60: 100] = 2
    gridray[80:140, 0: 100] = 2

    # create the part of scrubland in canyon
    gridray[20:140, 120:130] = 3

    # create the part of lake :
    gridray[70:80, 20:100] = 1

    # create the part of town :
    gridray[175:185, 75:85] = 8



    # initial the condition: start firing on power plant here:

    for i in range(0, 50):
        x = random.randint(189, 199)
        y = random.randint(0, 10)
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
run_once = 0
windDirection = "north"


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # YOUR CODE HERE

    updateBurn(grid, neighbourstates, neighbourcounts)

    return grid


# the function of firing chaparall simulation:

def generateProbability(grid, neighbourstates, burningNeighbourCount):
    probability_0 = np.where(grid == 0, 0.07 * burningNeighbourCount, 0)
    probability_2 = np.where(grid == 2, 0.0175 * burningNeighbourCount, 0)
    probability_3 = np.where(grid == 3, 0.6 * burningNeighbourCount, 0)
    probability_all = probability_0 + probability_2 + probability_3

    # unpack the state arrays
    NW, N, NE, W, E, SW, S, SE = neighbourstates
    northBurning = (N == 6)
    southBurning = (S == 6)
    eastBurning = (E == 6)
    westBurning = (W == 6)
    northwestBurning = (NW == 6)
    northeastBurning = (NE == 6)
    southwestBurning = (SW == 6)
    southeastBurning = (SE == 6)

    # array of pixels with a northern pixel that is burning

    if windDirection == "north":
        probability_all_W = np.where(northBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(southBurning, probability_all_W * 0.5, probability_all_W)

    elif windDirection == "south":
        probability_all_W = np.where(southBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(northBurning, probability_all_W * 0.5, probability_all_W)

    elif windDirection == "east":
        probability_all_W = np.where(eastBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(westBurning, probability_all_W * 0.5, probability_all_W)

    elif windDirection == "west":
        probability_all_W = np.where(westBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(eastBurning, probability_all_W * 0.2, probability_all_W)

    elif windDirection == "northwest":
        probability_all_W = np.where(northwestBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(southeastBurning, probability_all_W * 0.5, probability_all_W)

    elif windDirection == "northeast":
        probability_all_W = np.where(northeastBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(southwestBurning, probability_all_W * 0.5, probability_all_W)

    elif windDirection == "southwest":
        probability_all_W = np.where(southwestBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(northeastBurning, probability_all_W * 0.5, probability_all_W)

    elif windDirection == "southeast":
        probability_all_W = np.where(southeastBurning, probability_all * 2.5, probability_all)
        probability_all_W = np.where(northwestBurning, probability_all_W * 0.5, probability_all_W)

    else:
        probability_all_W = probability_all

    return probability_all_W


def updateBurn(grid, neighbourstates, neighbourcounts):


    randomNumber = np.random.rand(200, 200)
    toBurn = generateProbability(grid, neighbourstates, neighbourcounts[6]) > randomNumber

    burning = (grid == 6) | (grid == 4) | (grid == 7) | (grid == 5)

    itemindex = np.where(burning == True)
    timeTrack[itemindex] += 1

    toOrange = ((timeTrack == random.randint(75,85)) & (gridray == 2)) | (
                (timeTrack == random.randint(1, 2)) & (gridray == 3)) | (
                       (timeTrack == random.randint(20, 30)) & (gridray == 0)) | (
                           (timeTrack == random.randint(20, 30)) & (gridray == 6))
    toRed = ((timeTrack >= random.randint(250, 256)) & (gridray == 2)) | (
                (timeTrack >= random.randint(2,3 )) & (gridray == 3)) | (
                    (timeTrack >= 60) & (gridray == 0)) | ((timeTrack >= random.randint(59,60)) & (gridray == 6))
    stopBurn = ((timeTrack >= 720) & (gridray == 2)) | ((timeTrack >= 4) & (gridray == 3)) | (
            (timeTrack >= 166) & (gridray == 0)) | ((timeTrack >= 166) & (gridray == 6))

    grid[toBurn] = 6
    grid[toOrange] = 7
    grid[toRed] = 4
    grid[stopBurn] = 5

    global t
    t += 1
    if (run_once == 0) & ((grid == 8) & (neighbourcounts[6] >= 1)).any():
        printTime(t)


def printTime(t):
    print("The fire reached the town at: ", str(t))
    global run_once
    run_once += 1


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
