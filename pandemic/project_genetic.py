from GameObjects import *


def create_route(game_board):
    """
    Creates a valid route that encompasses all of the nodes.
    this is equivalent to randomly scrambling the board's _spaces list

    This is an implementation of the Nearest-Neighbor approach for TSP initial guess generation from p102 of Talbi

    """
    #     rest = game_board.city_names.copy()
    #     rest.remove("atlanta")

    #     print(["atlanta"] + random.sample(rest, game_board.num_cities - 1))
    #     return ["atlanta"] + random.sample(rest, game_board.num_cities - 1)

    path = ["atlanta"]
    cities = game_board.city_names.copy()  # The cities we need to visit
    #     print(cities)
    current_city = "atlanta"  # Every game starts with their players on Atlanta
    cities.remove("atlanta")
    while cities:
        neighbors = game_board.get_connections_as_BoardSpaces(current_city)
        current_city = random.choice(neighbors).name.lower()
        path.append(current_city)
        if current_city in cities:
            cities.remove(current_city)

    # Generate a random, VALID maximal independent set
    miset = nx.maximal_independent_set(game_board.get_graph())
    return path, miset


def create_initial_population(game_board, pop_size):
    """
    Creates an initial population of size popSize
    """
    population = []
    for _ in range(pop_size):
        population.append(create_route(game_board))
    return population


class GenomeEvaluator:
    """
    A class for the fitness function.
    We're using a class here instead of a function because it integrates well with Pandas DataFrames, as we'll see below
    """

    def __init__(self, route, mis, board: PandemicBoard):
        self.route = route
        self.board = board
        self.mis = mis
        self.distance = 0
        self.fitness = 0.0
        self.mis_penalty = 100

    def mis_cost(self):
        """
        All MISs created at the start of the run are valid.
        However, crossover/mutation might corrupt this.
        This function heavily penalizes invalid MIS elements, and otherwise returns better values for larger sets
        :return:
        """

        # Quickly verify whether or not the MIS is valid with the networkx package
        temp_set = []
        for city in self.mis:
            if self.board.is_mis_safe(city, set(temp_set)):
                temp_set.append(city)  # Adds the BSpace obj, not a string
            else:
                is_valid = False
                return self.mis_penalty
        else:  # complete the loop without breaking
            # Check the size and return a normalized score
            # MIS can't be greater than numcities/2
            valid_score = len(self.board.get_graph().nodes) / (2 * (1 + len(self.mis)))
            return valid_score

    def route_distance(self):

        if self.distance == 0:
            pathDistance = 0
            #             for i in range(0, len(self.route)):
            #                 fromCity = self.route[i]
            #                 toCity = None
            #                 if i + 1 < len(self.route):
            #                     toCity = self.route[i + 1]
            #                 else:
            #                     toCity = self.route[0]
            #                 pathDistance += fromCity.distance(toCity)

            # According to Wikipedia, we should weight this 1 if they are adjacent and 2 if they are not
            # https://en.wikipedia.org/wiki/Hamiltonian_path_problem
            route = self.route
            graph = self.board._nx
            missed_cities = self.board.city_names.copy()
            for i, city in enumerate(route):

                if city in missed_cities:
                    missed_cities.remove(city)

                # Find the destination from this link in the chain
                if i >= len(route) - 1:
                    # This is the last one; connect it to the origin (atlanta)
                    dest = "atlanta"
                else:
                    dest = route[i + 1]

                # Check if the two cities are neighbors

                if graph.has_edge(city, dest) or graph.has_edge(dest,
                                                                city):  # FIXME: About 95% positive has_edge is agnostic to order for an UDir graph
                    pathDistance += 1
                else:
                    #                     pathDistance += 2
                    #                     pathDistance += 2
                    shortest_path = self.board.shortest_path_lengths[city][
                                        dest] + 1  # Extra penalty to encourage the board to return adjacent nodes
                    pathDistance += shortest_path

            # Assess a penalty for each city that's not in there
            pathDistance += 25 * len(missed_cities)

            # Save the distance
            self.distance = pathDistance
        return self.distance

    def fitness_function(self):
        if self.fitness == 0:
            # We wish to minimize the distance, so return the inverse of the distance
            self.fitness = 1 / float(self.route_distance())
        total_score = self.fitness + self.mis_cost()
        return total_score


def evaluate_population(population, board):
    # Helper function that will sort a population in-place based on the fitness evaluator defined above
    results = {}
    for i, (path, mis) in enumerate(population):
        results[i] = GenomeEvaluator(path, mis, board).fitness_function()
    #     print("Evaluated pop: ", sorted(results.items(), key = operator.itemgetter(1), reverse = True))
    return sorted(results.items(), key=operator.itemgetter(1), reverse=True)


def select_parent_indices(sorted_pop, elite_ratio=0.25):
    """
    Select the next generation;s parents, with elite_ratio dictating how many pops make it based entirely on merit
    returns the relevant indices
    """
    results = []
    #     print("selection start len: ", len(sorted_pop) )

    elites = floor(len(sorted_pop) * elite_ratio)  # number of elements which will be merit-chosen

    df = pd.DataFrame(np.array(sorted_pop), columns=["Index", "Fitness"])
    df['cumulative_sum'] = df.Fitness.cumsum()
    df['cumulative_percentage'] = 100 * df.cumulative_sum / df.Fitness.sum()

    for i in range(0, elites):
        results.append(sorted_pop[i][0])
    for i in range(0, len(sorted_pop) - elites):
        pick = 100 * random.random()
        for i in range(0, len(sorted_pop)):
            if pick <= df.iat[i, 3]:
                results.append(sorted_pop[i][0])
                break
    #     print("selection end len: ", len(sorted_pop) )

    return results


def extract_parents(population, indexes):
    """
    Helper function to return the parents given a set of selection indices
    """
    #     print(sorted_pop)
    #     print((indexes))
    out = []

    for i in indexes:
        out.append(population[i])
    #     print(len(out))
    return out


def breed(x, y):
    """
    Breeds a child (c) using ordered crossover of genetic material from a and b
    """
    #     print("parent a is", a)
    c = ["atlanta"]
    a = x[0].copy()
    b = y[0].copy()
    a.remove("atlanta")
    b.remove("atlanta")

    length = len(a) - 1

    # Initialize lists for each parent's contributions
    a_c = []
    b_c = []

    # PATH CROSSOVER
    # Select a random point for each parent
    gene_1 = int(random.random() * length)
    gene_2 = int(random.random() * length)

    start = min(gene_1, gene_2)
    end = max(gene_1, gene_2)

    for i in range(start, end):
        a_c.append(a[i])
    # The rest come from B
    b_c = [item for item in b if item not in a_c]

    c += a_c + b_c
    #     print("child is ", c)
    return c


# Multisequence helper function for ID'ing common sequences between two lists
# Pulled from here: https://stackoverflow.com/questions/32318113/find-all-common-sequences-of-two-list-in-python
def matches(list1, list2):
    while True:
        mbs = difflib.SequenceMatcher(None, list1, list2).get_matching_blocks()
        if len(mbs) == 1: break
        for i, j, n in mbs[::-1]:
            if n > 0: yield list1[i: i + n]
            del list1[i: i + n]
            del list2[j: j + n]


def breed_variable_length(x, y, board: PandemicBoard):
    # print(x)
    a = x[0].copy()
    b = y[0].copy()
    c = []

    # PATH CROSSOVER
    # Attempt single-point crossover
    smaller_len = min(len(a), len(b))
    cross_pt = random.randint(0, smaller_len)
    c1 = a[:cross_pt]
    c2 = b[cross_pt:]
    c = c1 + c2
    #     d = c.copy()
    # Scrub out duplicates that are RIGHT next to each other
    d = [c[i] for i in range(len(c)) if (i == 0) or c[i] != c[i - 1]]

    # "Fill" the path
    # Verify that each child is "stitched together" i.e

    # "Scroll back the path"
    # Since all paths need to start and end at atlanta, we'll move "atlanta" to the front and then "roll back" the other steps

    try:
        atlanta_index = d.index("atlanta")
        e = []
        for i in range(atlanta_index):
            e.append(d[i])
        # return d[atlanta_index:] + e
        d = d[atlanta_index:] + e

    except ValueError:
        # Atlanta is not in there
        pass

    # return c
    # MIS CROSSOVER
    # simply doing a single-point crossover is unlikely to work with MIS
    # thus, we'll merge the two - i.e., we'll iterate through the smaller and add it to the larger if it doesn't invalidate the set
    smaller_mis = min(x[1], y[1], key=lambda x: len(x))
    larger_mis = max(x[1], y[1], key=lambda x: len(x))
    # print(larger_mis)
    for city_name in smaller_mis:
        if city_name in larger_mis:
            continue
        else:
            if board.is_mis_safe(city_name, set(larger_mis)):
                larger_mis.append(city_name)

    return d, larger_mis


def breed_population(matingpool, elite_ratio, board):
    children = []
    elites = floor(elite_ratio * len(matingpool))
    length = len(matingpool) - elites
    pool = random.sample(matingpool, len(matingpool))

    for i in range(elites):
        children.append(matingpool[i])

    for i in range(length):
        child = breed_variable_length(pool[i], pool[len(matingpool) - i - 1], board)
        children.append(child)

    #     print("Made ", len(children), " kids.")
    return children


def mutate_individual(individual: tuple[list, set], mutation_rate, board: PandemicBoard) -> tuple[list, set]:
    """
    Mutate an individual using the provided mutation ratio
    """
    path, mis = individual
    for i, chromosome in enumerate(path):
        mutation_chance = random.random()
        if mutation_chance < mutation_rate:
            # The chromo needs to be mutated. Find a random element to swap with
            # flip a coin to see if it's in the path or the mis
            swapee = int(random.random() * len(path))

            # Execute the swap
            a = path[i]
            b = path[swapee]

            path[i] = b
            path[swapee] = a

    for i, chromosome in enumerate(mis):
        mutation_chance = random.random()
        if mutation_chance < mutation_rate:
            swap_out = random.choice(mis)
            # Quick disjoint one-liner from here:
            # https://stackoverflow.com/questions/13672543/removing-the-common-elements-between-two-lists
            swap_in = random.choice(list(set(board.get_city_names()) ^ set(mis)))
            mis.remove(swap_out)
            mis.append(swap_in)

    return path, mis


def mutate_population(population, mutation_rate, board):
    out = []

    for i, genome in enumerate(population):
        processed_genome = mutate_individual(genome, mutation_rate, board)
        out.append(processed_genome)

    return out


# Additional helper to combine all of the steps into one function
def build_next_generation(current_generation, elite_ratio, mutation_rate, board):
    # Execute every step sequentially
    # evaluate, select, breed, mutate
    scores = evaluate_population(current_generation, board)
    selected_genomes = select_parent_indices(scores, elite_ratio)
    parents = extract_parents(current_generation, selected_genomes)
    children = breed_population(parents, elite_ratio, board)
    next_generation = mutate_population(children, mutation_rate, board)

    return next_generation


from time import sleep


def main(board, initial_pop_size, elite_ratio, mutation_rate, num_generations):
    # Generate the inital pop
    progress = []
    population = create_initial_population(board, initial_pop_size)
    #     print(population)
    print("Initial distance: ", str(evaluate_population(population, board)[0][1]))
    # Steps
    sleep(.2)
    queue = tqdm(range(num_generations), desc="Progress: ")
    for step in queue:
        population = build_next_generation(population, elite_ratio, mutation_rate, board)
        best_score = evaluate_population(population, board)[0][1]
        print(best_score)
        queue.desc = "Progress (Best score: {:.2f},  popsize: {}): ".format(
            best_score, len(population))

        progress.append(best_score)
        # Check if we can break
    #         if 50 < best_score < 60:
    #             print("Optimal range detected. Breaking...")
    #             break
    #         print(population[0])
    #         input()
    # report final distance
    print("Final distance: ", str(1 / evaluate_population(population, board)[0][1]))

    best_route_index = evaluate_population(population, board)[0][0]

    best_route = population[best_route_index]
    #     print(population)

    return best_route, progress


def stitch(board, route):
    """
    'Stitch together' the final result
    Basically, this is realizing the penalty for having two non-adjacent nodes be in the path by filling in the intermediate nodes to the final path

    """
    out = []
    a = 0
    graph = board._nx
    for i, city in enumerate(route):

        # Find the destination from this link in the chain
        if i >= len(route) - 1:
            # This is the last one; connect it to the origin (atlanta)
            dest = "atlanta"
        else:
            dest = route[i + 1]

        # Check if the two cities are neighbors

        if graph.has_edge(city, dest) or graph.has_edge(dest,
                                                        city):  # FIXME: About 95% positive has_edge is agnostic to order for an UDir graph
            continue
        else:
            intermediaries = board.shortest_paths[city][dest]
            #             print(intermediaries)
            out += route[a:i]
            out += intermediaries
            a = i

    return out


if __name__ == "__main__":
    # CLI interface
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--elitepct", type=float,
                        help="The % of each generation that should carry over from the most fit of the gen, as a decimal (default 0.3)",
                        default=0.3)
    parser.add_argument("-m", "--mrate", type=float, help="The mutation rate, as a decimal value (default 0.002)",
                        default=0.002)
    parser.add_argument("-p", "--popsize", type=int, help="The population size of each generation (default 100)",
                        default=100)
    parser.add_argument("-n", "--ngens", type=int, help="How many iterations of the GA to run (default 500)",
                        default=500)
    parser.add_argument("-s", "--save", type=str, help="Whether or not to save the results to a file",
                        default="ga_output.json")

    args = parser.parse_args()

    # Create board and run
    board = PandemicBoard("./data/pandemic_board.csv")
    #     best_path, progress = main(board, 150, 0.25, 0.01, 1000)
    results, progress = main(board, args.popsize, args.elitepct, args.mrate, args.ngens)

    best_path, mis = results

    print("Original Best Path: \n\n", best_path)

    # Stitch the best path together
    best_path = stitch(board, best_path)

    print("Best Path: \n\n", best_path)
    print()
    print("Length of Best Path: ", len(best_path))
    print()


    # diff = list(set(board.city_names) - set(best_path)) + list(set(board.city_names) - set(best_path))

    def Diff(li1, li2):
        return list(set(li1) - set(li2)) + list(set(li2) - set(li1))


    print("Missed Cities: \n", Diff(board.city_names, best_path))
    print()

    print("=== MIS ===")
    print("MIS Length: ", len(mis))
    print("Selected MIS: \n", mis)
    print("MIS Validity: ", end="")
    oofs = []
    oof_city = ""
    for city in mis:
        mis.remove(city)
        if board.is_mis_safe(city, mis):
            mis.append(city)
        else:
            for e in mis:
                if city in board[e].get_connections_as_strings():
                    oofs.append(e)
            mis.append(city)
            valid = False
            oof_city = city
            break
    else:
        valid = True
    if not valid:
        print("False ({} connects with {})".format(oof_city, oofs))
    else:
        print("True")

    # Prompt for the go-ahead for a pop-up
    input("Press ENTER to see a visualization of the algorithm's training progress.\n"
          "Close the pop-up window to exit this application.")

    plt.plot(progress)
    plt.ylabel('Cost')
    plt.xlabel('Generation')
    plt.show()
