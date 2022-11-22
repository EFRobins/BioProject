# Name: hongyu_simulation1
# Dimensions: 2

# --- Set up executable path, do not edit ---
import random
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
    # State 4: state of chaparral burning
    # State 5: state of death / stop burning
    # State 6: state of dense forest burning
    # State 7: state of scrubland burning

    config.states = (0, 1, 2, 3, 4, 5)
    config.wrap = False
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.7, 0.7, 0.2), (0.4, 0.8, 1), (0.3, 0.4, 0),
                           (0.9, 1, 0), (0.7, 0, 0.1), (0.4, 0.4, 0.4)]


    global geneNum
    geneNum = config.num_generations
    # countNum = 0
    config.grid_dims = (200, 200)
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


    # for y in range(0, 3):
    #     for x in range(0, 100):
    #         gridray[y][x] = 4

    # randomly pick 50 cells up from 10 * 10 square on the left top map:

    for i in range(0, 50):
        x = random.randint(0, 10)
        y = random.randint(0, 10)
        gridray[y][x] = 4



    # for y in range(0, 1):
    #     for x in range(194, 200):
    #         gridray[y][x] = 4


    config.set_initial_grid(gridray)

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # YOUR CODE HERE

    relativeTime_simu(grid, neighbourstates, neighbourcounts)

    return grid


def relativeTime_simu(grid, neighbourstates, neighbourcounts):
    # ----------------------Simulate the chaparral with wind exist------:

    # unpack the state arrays as diff directions:
    NW, N, NE, W, E, SW, S, SE = neighbourstates
    # anything which is burning:
    isburning = (grid == 4)

    # get the cells that have a north burning neig:
    NorthDirctIsburing = (N == 4)
    chaparralsAllowedStart_burning = (grid == 0) & (grid != 5)
    # the condition of start burning that start burning when have a nei is burning in north:
    chaparrals_BurningNei_withWind = (neighbourcounts[4] > 1)
    # the condition of start burning:
    chaparrals_BurningNei = (neighbourcounts[4] > 2)

    ruleONE_chap = chaparralsAllowedStart_burning & chaparrals_BurningNei
    ruleTWO_chap = chaparralsAllowedStart_burning & (chaparrals_BurningNei_withWind
                                                     & NorthDirctIsburing)

    chaparrals_startBurning = (ruleTWO_chap | ruleONE_chap)

    # ---------------------Simulate the dense forest with wind exist------:

    denseForestAllowedStart_burning = (grid == 2) & (grid != 5)
    # the condition of start burning:
    denseForest_BurningNei = (neighbourcounts[4] >= 5)
    # the condition of start burning that start burning when have a nei is burning in north:
    denseForest_BurningNei_withWind = (neighbourcounts[4] >= 4 )

    ruleONE_denseF = denseForestAllowedStart_burning & denseForest_BurningNei
    ruleTWO_denseF = denseForestAllowedStart_burning & (denseForest_BurningNei_withWind
                                                        & NorthDirctIsburing)
    denseForest_startBurning = (ruleONE_denseF | ruleTWO_denseF)

    # ---------------------Simulate the scrubland in canyon with wind exist------:

    scrublandAllowedStart_burning = (grid == 3) & (grid != 5)
    scrubland_BurningNei_withWind = (neighbourcounts[4] > 1)
    scrubland_BurningNei = (neighbourcounts[4] > 2)

    ruleONE_scru = scrublandAllowedStart_burning & scrubland_BurningNei
    ruleTWO_scru = scrublandAllowedStart_burning & (scrubland_BurningNei_withWind
                                                     & NorthDirctIsburing)

    scrubland_startBurning = (ruleTWO_scru | ruleONE_scru)

    itemindex = np.where(isburning == True)
    timeTrack[itemindex] += 1
    # geneNum is the whole timeline from the setup function:
    # "(timeTrack >= geneNum/5) " is the time that chaparrals can be burning.
    # "((timeTrack >= (geneNum/5)/24)" is the time that grassland in canyon can be burning.
    # "(timeTrack >= (geneNum*2)/5)" is the time that dense forest can be burning.

    stopBurn = (((timeTrack >= geneNum/5) & (gridray == 0)) |
                ((timeTrack >= (geneNum/5)/24) & (gridray == 3)) |
                ((timeTrack >= (geneNum*2)/5) & (gridray == 2)))
    grid[denseForest_startBurning | chaparrals_startBurning
         | scrubland_startBurning] = 4
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
