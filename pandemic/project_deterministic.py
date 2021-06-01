import os
import pandemic
from GameObjects import *

def tsp_candidate(board: PandemicBoard, current_vertex: str, current_path: str) -> bool:
    previous_vertex = current_path[-1]

    # Check if the potential addition to the path is a valid neighbor
    if current_vertex in board[previous_vertex].get_connections_as_strings():
        return False

    # Check if the potential addition is already in the path
    elif current_vertex in path:
        return False
    else:
        return True

def continue_tsp(board: PandemicBoard, path):
    """
    Continuation function for if the MIS has completed, but we need to keep on moving on the TSP
    :param board:
    :param path:
    :return:
    """
    pass

def continue_mis(board:PandemicBoard, path):
    """
    Continuation function for if the TSP has completed, but we need to keep moving on the MIS
    :param board:
    :param path:
    :return:
    """
    pass

def mis_with_backtracking(board: PandemicBoard, path) -> (list[str], list[str]):
    """
    Deterministically run a DFS for a hamiltonian cycle, tracking the MIS simultaneously with backtracking
    :param board:
    :param path:
    :return:
    """
    # Base Case - Given Graph
    # has no nodes
    if (len(board) == 0):
        return [], path

    # Base Case - Given Graph
    # has 1 node
    if (len(board) == 1):
        return [board[0].name], path

    # Select a vertex from the graph
    vCurrent = board[0].name

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
    res1 = mis_with_backtracking(graph2, path)[0]
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
    res2 = [vCurrent] + mis_with_backtracking(graph2, path)[0]

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