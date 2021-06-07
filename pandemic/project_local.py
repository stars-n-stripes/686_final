import os
import pandemic
from GameObjects import *
import tqdm
from project_genetic import create_route
from random import choice, random, randint

# Implementation of a local search for the problem
def select_neighboring_path(board, in_path):
    # TODO: how to we shorten the path?
    path = in_path.copy()
    swap_start = randint(0, len(path) - 3) # At the worst, we want at least two cities to switch
    swap_end = randint(swap_start + 1, len(path))
    #Reverse the paths with a slice
    path[swap_start:swap_end] = path[swap_start:swap_end:-1]
    return path


def simulated_annealing_path(board: PandemicBoard, cooling_rate, starting_temp, ending_temp):
    # Following a guide here;
    # https://toddwschneider.com/posts/traveling-salesman-with-simulated-annealing-r-and-shiny/
    temperature = starting_temp

    while temperature > ending_temp:

        # Generate a random original path
        path = create_route(board)[0]

        # Score it - lower is better
        score = len(path) * missing_ciites_in_path(board, path) + len(path)

        # select a neighboring tour
        """
        Pick a new candidate tour at random from all neighbors of the existing tour. Via Professor Joe Chang, one way to 
        pick a neighboring tour “is to choose two cities on the tour randomly, and then reverse the portion of the tour that
         lies between them.” This candidate tour might be better or worse compared to the existing tour, i.e. shorter or 
         longer.
         http://www.stat.yale.edu/~pollard/Courses/251.spring2013/Handouts/Chang-MoreMC.pdf
        """
        neighbor = select_neighboring_path(board, path)
        neighbor_score = len(neighbor) * missing_ciites_in_path(board, neighbor) + len(neighbor)

        # Compare the two and select the better
        if neighbor_score < score:
            # Neighbor is better. Always accept it
            winner = neighbor
            winning_score = neighbor_score
        else:

            # Check if we actually follow that or - because of the heat - accept the worse result anyway
            temp_check = random()
            if temp_check < temperature:
                # Heat causes suboptimal move
                winner = neighbor
                winning_score = neighbor_score
            else:
                winner = path
                winning_score = score

        # Cool down
        temperature -= cooling_rate
    return path






def missing_ciites_in_path(board, path):
    """
    Returns the number of cities missing from the path
    :param board:
    :param path:
    :return:
    """

    missed_cities = board.city_names.copy()
    for i, city in enumerate(path):

        if city in missed_cities:
            missed_cities.remove(city)

    return len(missed_cities)

def simulated_annealing_mis(board):
    # Same guide

    # Generate a random MIS
    # Create_route is a misnomer, this is being borrowed from the GA code module.
    path = create_route(board)[1]


if __name__ == '__main__':
    board = PandemicBoard("./data/europe_board_cycle.csv")
    p =simulated_annealing_path(board, starting_temp=0.85, cooling_rate=0.085, ending_temp=0.125)
    print(p)
    print(missing_ciites_in_path(board, p))