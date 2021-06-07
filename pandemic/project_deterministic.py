import os
import pandemic
from GameObjects import *

def tsp_candidate(board: PandemicBoard, current_vertex: str, current_path: str) -> bool:
    previous_vertex = current_path[-1]

    # Check if the potential addition to the path is a valid neighbor
    if current_vertex not in board[previous_vertex].get_connections_as_strings():
        return False

    # Check if the potential addition is already in the path
    elif current_vertex in current_path:
        return False
    else:
        return True

def continue_mis(board: PandemicBoard, path):
    """
    Continuation function for if the MIS has completed, but we need to keep on moving on the TSP
    :param board:
    :param path:
    :return:
    """
    pass

def continue_tsp(board:PandemicBoard, path):
    """
    Continuation function for if the TSP has completed, but we need to keep moving on the MIS
    :param board:
    :param path:
    :return:
    """
    # Base case - board has only one node
    # (this function will not get called with an empty board)
    if len(board.get_city_names()) == 0:
        # print("\t\tBreaking...")
        return path

    last_city = board[path[-1]]
    # First, check if THIS city is valid
    if tsp_candidate(board, last_city, path):
        # print("\t\tAdding ", last_city.name)
        path.append(last_city.name)
        if path_has_all_nodes(board, path):
            return path

    for neighbor in last_city.get_connections_as_strings():
        # print("\t\tLooking at neighbor: ", neighbor)
        if tsp_candidate(board, neighbor, path):
            path.append(neighbor)
            # DFS recursive call
            path = continue_tsp(board, path)
            if path_has_all_nodes(board, path):
                # print("\t\t\tDFS complete for HC")
                break # we're done

    return path



def path_has_all_nodes(board, path):
    """
    Verifies whether or not the path is actually a complete hamiltonian cycle
    :param board:
    :param path:
    :return:
    """
    if set(x for x in board.spaces()) - set(path):
        # spaces remain
        return False
    return True


def mis_with_backtracking(board: PandemicBoard, path, original_board: PandemicBoard=None):
    """
    Deterministically run a DFS for a hamiltonian cycle, tracking the MIS simultaneously with backtracking
    Adapted from an example on GeeksForGeeks
    https://www.geeksforgeeks.org/maximal-independent-set-in-an-undirected-graph/
    :param board:
    :param path:
    :return:
    """
    # First iteration, remember the original state of the board for DFS-HC
    if not original_board:
        original_board = board.copy()


    # Base Case - Given Graph
    # has no nodes
    if (len(board) == 0):
        # We hit the end of the road
        return [], path

    # Base Case - Given Graph
    # has 1 node
    if (len(board) == 1):
        # We hit the end of the road, BUT, if the path is still not complete, we can continue the DFS for the path
        if not path_has_all_nodes(original_board, path):

            # print("\tContinuing DFS for HC from {}...".format(board[0].name))
            path = continue_tsp(original_board, path)
        return [board[0].name], path

    # Select a vertex from the graph
    vCurrent = board[0].name
    # print("Visiting ", vCurrent)

    if vCurrent not in path:
        path.append(vCurrent)

    # Case 1 - Proceed removing
    # the selected vertex
    # from the Maximal Set
    graph2 = board.copy()

    # Delete current vertex
    # from the Graph
    graph2.remove(vCurrent)

    # Recursive call - Gets
    # Maximal Set,
    # assuming current Vertex
    # not selected
    res1, temp_path = mis_with_backtracking(graph2, path, original_board)
    if len(temp_path) > len(path):
        path = temp_path
    # print(res1)

    # Case 2 - Proceed considering
    # the selected vertex as part
    # of the Maximal Set

    # Loop through its neighbours
    for v in board[vCurrent].get_connections_as_strings():

        # Delete neighbor from
        # the current subgraph
        if (v in graph2):
            graph2.remove(v)

    # This result set contains VFirst,
    # and the result of recursive
    # call assuming neighbors of vFirst
    # are not selected
    # print(mis_with_backtracking(graph2, path)[0])
    g2 = mis_with_backtracking(graph2, path, original_board)
    res2, temp_path = [vCurrent] + g2[0], g2[1]
    if len(temp_path) > len(path):
        path = temp_path

    # Our final result is the one
    # which is bigger, return it
    if (len(res1) > len(res2)):
        return res1, path
    return res2, path

if __name__ == '__main__':
    board = PandemicBoard("./data/europe_board_cycle.csv")
    maximalIndependentSet, path = mis_with_backtracking(board, list())

    # Prints the Result
    for i in maximalIndependentSet:
        print(i, end=" ")

    print("\n")
    for i in path:
        print(i, end="->")
    else:
        print('\b\b')