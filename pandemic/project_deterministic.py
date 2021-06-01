import os
import pandemic
from GameObjects import *


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
    board = PandemicBoard("./data/europe_board.csv")
    maximalIndependentSet, path = mis_with_backtracking(board, list())

    # Prints the Result
    for i in maximalIndependentSet:
        print(i, end=" ")

    print("\n")
    for i in path:
        print(i, end="->")
    else:
        print('\b\b')