import numpy as np
import pandas as pd
import random
import operator
import matplotlib.pyplot as plt
from enum import Enum
from csv import DictReader
import networkx as nx
from math import floor
from tqdm import tqdm
import difflib
from sys import argv
from copy import deepcopy
import argparse


class Disease(Enum):
    RED = 0
    YELLOW = 1
    BLUE = 2
    BLACK = 3


class PlayerClasses(Enum):
    RESEARCHER = 0


class Player:
    numplayers = 0

    def __init__(self, board, player_class=None):
        self.player_class = player_class
        self.pid = Player.numplayers + 1
        Player.numplayers += 1
        self._board = board
        self.location = None


class Card:
    def __init__(self, name, color):
        self.name = name
        self.color = color


class CityCard(Card):
    pass


class EffectCard(Card):
    def __init__(self, name, color, text):
        self.text = text
        super().__init__(name, color)


class BoardSpace:
    def __init__(self, name, color, players=None, connections=None,research_staiton=False, **kwargs):

        if connections:
            self.connections = connections
        else:
            self.connections = []

        if players == None:
            self.players = []
        elif isinstance(players, Player):
            self.players = [players]
        else:
            self.players = players

        self.name = name
        self.diseases = dict()
        for dname in Disease.__members__.keys():
            ln = dname.lower()
            if ln in kwargs.keys():
                self.diseases[ln] = kwargs[ln]
            else:
                self.diseases[ln] = 0
        # Remember if a player is there.
        self.color = color
        # Boolean for research station
        self._research_station = research_staiton

    def get_connections_as_strings(self):
        return self.connections

    def add_station(self):
        self._research_station = True

    def has_station(self):
        return self._research_station

    def remove_station(self):
        self._research_station = False



    def _connstr(self):
        cstr = ""
        for c in self.connections:
            cstr += c + ", "
        # cut out the final comma
        cstr = cstr[:-2]
        return cstr

    def __str__(self):

        cstr = self._connstr()

        out = "[BoardState {} / {} Players / Diseases: {} red,{} yellow, {} blue, {} black] -> ({})".format(
            self.name,
            len(self.players),
            self.diseases["red"],
            self.diseases["blue"],
            self.diseases["yellow"],
            self.diseases["black"],
            cstr

        )

        return out

    def __repr__(self):

        cstr = self._connstr()

        out = "bstate{{{}/{}p/{}r/{}y/{}bu/{}bk -> ({})}}".format(
            self.name,
            len(self.players),
            self.diseases["red"],
            self.diseases["blue"],
            self.diseases["yellow"],
            self.diseases["black"],
            cstr

        )

        return out


class PandemicBoard:
    def __init__(self, boardFile):

        self._spaces = []
        self.players = []
        self.discard = []
        self.infection_deck = []
        self.discard = []

        # Open the board and read it
        with open(boardFile, "r", encoding="UTF-8") as pbfile:
            pbReader = DictReader(pbfile)
            for row in pbReader:
                #                 print(row)
                name = row["city_name"].lower()
                color = row["color"].lower()
                if not row["players"] or row["players"] == "0":
                    players = None
                else:
                    players = []
                    for intchar in row["players"]:
                        if int(intchar) > Player.numplayers:
                            p = Player(self)  # update one day if we want to put player classes in
                            self.players.append(p)
                            players.append(p)
                        else:
                            # Find and add an existing player to the board space
                            p = self.get_player(int(intchar))
                            players.append(p)
                diseases = {}
                for dname in Disease.__members__.keys():
                    if dname.lower() in row.keys():
                        # check if the disease is present
                        dnum = int(row[dname.lower()])
                        diseases[dname.lower()] = dnum

                # Find and log connections
                connections = row["connections"].split(";")

                # Detect if there's a research station there
                research_station = bool(int(row["research_station"]))  # e.g., Casts a "0" stirng to an int, then False

                # make the space
                #                 print("New BoardSpace with name {}, {} players, and disease concentrations Red: {}, Blue: {}, Yellow: {}, Black: {}"
                #                       .format(name, len(players) if isinstance(players, list) else 0, diseases["red"], diseases["blue"], diseases["black"], diseases["yellow"])) # debug
                #                 print("Space is connected to: ")
                #                 for x in connections:
                #                     print("\t", x)

                b = BoardSpace(name, color, players, connections,research_station, **diseases)
                self._spaces.append(b)
        # Finally, generate a graph representation for viz and running the GA
        self._nx, self.shortest_path_lengths, self.shortest_paths = self.gen_networkx()
        #         print(self._nx)

        # helper attributes
        self.city_names = [city.name for city in self._spaces]
        self.num_cities = len(self.city_names)

    def __getitem__(self, key):

        if isinstance(key, int):
            return self._spaces[key]

        for element in self._spaces:
            if element.name == key:
                return element
        else:
            raise KeyError("Key \"{}\" not present in board".format(key))

    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p

    def spaces(self):
        for s in self._spaces:
            yield s

    def get_connections_as_BoardSpaces(self, target_name):
        c = self[target_name].get_connections_as_strings()
        out = []
        for conn in c:
            out.append(self[conn])
        return out

    def gen_networkx(self):
        # To be called at the end of __init__, this function creates a Networkx representation of the board
        g = nx.Graph()
        g.add_nodes_from([s.name for s in self._spaces])  # Add the nodes themselves
        for city in self._spaces:
            for conn in city.get_connections_as_strings():
                #                 print(conn)
                g.add_edge(city.name, conn)

        # Build the shortest paths
        g_shortest_path_lengths = dict(nx.all_pairs_shortest_path_length(g))
        g_shortest_paths = dict(nx.all_pairs_shortest_path(g))
        return g, g_shortest_path_lengths, g_shortest_paths

    def get_graph(self):
        """
        Returns the networkx graph
        :return:
        """
        return self._nx

    def get_city_names(self):
        return self.city_names

    def copy(self):
        return deepcopy(self)

    def remove(self, city):
        if isinstance(city, str):
            # locate city by string
            self._nx.remove_node(city)
            for i in range(len(self._spaces)):
                if self[i].name == city:
                    del (self._spaces[i])
                    break
            else:
                raise ValueError("City passed for deletion in PandemicBoard.remove() not present in board")
        elif isinstance(city, BoardSpace):
            self._nx.remove_node(city.name)
            for i in range(len(self._spaces)):
                if self[i].name == city.name:
                    del (self._spaces[i])
                    break
            else:
                raise ValueError("City passed for deletion in PandemicBoard.remove() not present in board")
        else:
            raise TypeError("PandemicBoard.remove() only accepts arguments of type str or BoardSpace")

    def show_viz(self):
        #         nx.draw_networkx(self._nx, nx.random_layout(self._nx))
        #         nx.draw_networkx_labels(self._nx, nx.spring_layout(self._nx))

        plt.figure(num=None, figsize=(20, 20), dpi=80)
        plt.axis('off')
        fig = plt.figure(1)
        pos = nx.spring_layout(self._nx)
        nx.draw_networkx(self._nx, pos)

    def is_mis_safe(self, space, solution_set_names: set):
        """
        Returns true if the set is safe for the MIS detailed in the solution set provided, false otherwise.
        NOTE: solution_set is set(str)
        """
        if isinstance(space, str):
            for city in solution_set_names:
                if space in self[city].get_connections_as_strings():
                    return False
            else:
                return True

        elif isinstance(space, BoardSpace):
            for city in solution_set_names:
                if space.name in self[city].get_connections_as_strings():
                    return False
            else:
                return True



