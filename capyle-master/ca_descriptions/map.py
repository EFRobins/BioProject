# Name: NAME
# Dimensions: 2


import numpy as np
import inspect
# --- Set up executable path, do not edit ---
import sys

this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils

# ---


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "MAP"
    config.dimensions = 2
    config.states = (0, 1, 2, 3, 4, 5, 6, 7)
    config.num_generations = 100
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # config.state_colors = [(0,0,0),(1,1,1)]
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------
    config.state_colors = [(0.6,0.9,0), (1, 1, 0),(0.3, 0.7, 0), (0.9, 0.6, 0.1), (0.1, 0.5, 0),(0.7, 0, 0),(0.3, 0.3, 0.3), (0.2, 0, 0.5) ]
    # 1- grass 2- burning grass 3- chaparral 4- burning chaparral 5- forest 6- burning forest 7- ash 8- water  
    config.grid_dims = (200, 200)
    gridray = np.zeros((200, 200))

    for y in range(0, 200):
        for x in range(0, 200):
            gridray[y][x] = 2
    
    for y in range(20,70):
        for x in range(60, 100):
            gridray[y][x] = 4

    for y in range(70,80):
        for x in range(20,100):
            gridray[y][x] = 7
    
    for y in range(80,125):
        for x in range(0,100):
            gridray[y][x] = 4
    
    for y in range(20, 160):
        for x in range(120, 140):
            gridray[y][x] = 3
                    
    config.set_initial_grid(gridray)
    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # YOUR CODE HERE
    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
