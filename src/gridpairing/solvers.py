from __future__ import annotations
from .grid import Grid

class Solver:
    """
    Base solver class
    
    Attributes:
    -----------
    grid: Grid
        The grid instance containing values and colors.
    pairs: list
        A list of valid pairs, each being a tuple ((i1, j1), (i2, j2)).
    """

    def __init__(self, grid: Grid):
        """
        Initialize the solver with a grid.

        Parameters:
        -----------
        grid: Grid
            The input grid to solve.
        """
        self.grid = grid
        self.pairs = self.grid.all_pairs()

    def score(self):
        """
        Compute the total score of the selected pairs.

        Returns:
        --------
        int
            The total score of the current solution.
        """
        S = sum(self.grid.cost(pair) for pair in self.pairs)
        used_cells = {cell for pair in self.pairs for cell in pair}

        # Adds the value of unused cells
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                if not self.grid.is_forbidden(i, j) and (i, j) not in used_cells:
                    S += self.grid.value[i][j]

        return S


class SolverNaive(Solver):
    """
    A naive solver that selects valid pairs in ascending order of cost.
    
    Time Complexity: O(n * m log(n * m)) due to sorting.
    """

    def run(self):
        """
        Executes a naive solving strategy.

        The algorithm:
        1. Gets all valid pairs from the grid
        2. Sorts them by increasing cost
        3. Selects non-overlapping valid pairs until there are no more available

        Returns:
        --------
        int
            The total score of the selected pairs.
        """
        self.pairs = self.grid.all_pairs()
        self.pairs.sort(key=lambda x: self.grid.cost(x))
        used_cells = set()
        selected_pairs = []

        for pair in self.pairs:
            if pair[0] not in used_cells and pair[1] not in used_cells:
                used_cells.update(pair)
                selected_pairs.append(pair)

        self.pairs = selected_pairs
        return self.score()


class Graph:
    """
    A graph implementation for min-cost flow problems.
    
    This class represents a directed graph with capacities and costs
    on edges, designed for min-cost flow algorithms.
    
    Attributes:
    -----------
    capacity: dict
        Edge capacity mapping {u: {v: cap}}.
    cost: dict
        Edge cost mapping {u: {v: cost}}.
    flow: dict
        Current flow mapping {u: {v: flow}}.
    neigh: dict
        Set of neighbors for each node {u: {v1, v2, ...}}.
    adj_list: dict
        Adjacency list for faster traversal {u: [v1, v2, ...]}.
    """

    def __init__(self):
        """
        Initialize an empty graph for min-cost flow.
        """
        self.capacity = {}
        self.cost = {}
        self.flow = {}
        self.neigh = {}
        self.adj_list = {}

    def add_edge(self, u, v, cap, cost):
        """
        Add a directed edge to the graph with reverse edge.
        
        Parameters:
        -----------
        u: object
            Source node
        v: object
            Target node
        cap: int
            Edge capacity
        cost: int
            Edge cost
        """
        for node in [u, v]:
            if node not in self.capacity:
                self.capacity[node] = {}
                self.cost[node] = {}
                self.flow[node] = {}
                self.neigh[node] = set()
                self.adj_list[node] = []

        # Principal edge
        self.capacity[u][v] = cap
        self.cost[u][v] = cost
        self.flow[u][v] = 0
        self.neigh[u].add(v)
        self.adj_list[u].append(v)

        # Reciprocal edge
        self.capacity[v][u] = 0
        self.cost[v][u] = -cost
        self.flow[v][u] = 0
        self.neigh[v].add(u)
        self.adj_list[v].append(u)

    def bellman_ford(self, source, sink):
        """
        Runs a Bellman-Ford algorithm to find shortest paths.
        
        Uses a version optimized to end early when a path to the sink
        is found and uses a queue-based approach for performance.
        
        Parameters:
        -----------
        source: object
            Source node
        sink: object
            Sink node
            
        Returns:
        --------
        tuple
            (distances, predecessors) where distances is a dict mapping
            nodes to their shortest distance from source, and predecessors
            is a dict mapping nodes to their predecessor in the shortest path.
        """
        INF = float("inf")
        dist = {node: INF for node in self.capacity}
        pred = {node: None for node in self.capacity}
        dist[source] = 0
        
        # Queue initialization
        queue = [source]
        in_queue = {node: (node == source) for node in self.capacity}
                
        while queue:
            u = queue.pop(0)
            in_queue[u] = False
            
            # Uses an adjacency list to go through the neighbors quicker
            for v in self.adj_list[u]:
                if self.capacity[u][v] > self.flow[u][v]:
                    new_cost = dist[u] + self.cost[u][v]
                    if new_cost < dist[v]:
                        dist[v] = new_cost
                        pred[v] = u
                        if not in_queue[v]:
                            queue.append(v)
                            in_queue[v] = True
            
            # Stops search if sink is reached/if queue is empty
            if not queue and dist[sink] < INF:
                return dist, pred
                
        return dist, pred

    def min_cost_flow(self, source, sink):
        """
        Finds minimum cost flow from source to sink.
        
        Uses the successive shortest path algorithm with Bellman-Ford
        to find augmenting paths.
        
        Parameters:
        -----------
        source: object
            Source node
        sink: object
            Sink node
            
        Returns:
        --------
        tuple
            (total_cost, pairs) where total_cost is the minimum cost of the flow,
            and pairs is a list of (u, v) pairs where flow is sent.
        """
        pairs = []
        total_cost = 0

        while True:
            dist, pred = self.bellman_ford(source, sink)
            if dist[sink] == float("inf"):
                break  # No more augmenting paths

            # Calculates augmenting path
            path = []
            flow = float("inf")
            v = sink
            while v != source:
                u = pred[v]
                if u is None:
                    flow = 0
                    break
                path.append((u, v))
                flow = min(flow, self.capacity[u][v] - self.flow[u][v])
                v = u

            if flow == 0:
                break

            # Changes flow along the way
            for u, v in path:
                self.flow[u][v] += flow
                self.flow[v][u] -= flow
                total_cost += self.cost[u][v] * flow

        # Gives all the positive-flow pairs
        for u in self.capacity:
            if u == source or u == sink:
                continue
            for v in self.adj_list[u]:
                if v != source and v != sink and self.flow[u][v] == 1:
                    pairs.append((u, v))

        return total_cost, pairs


class SolverBellmanFord(Solver):
    """
    Grid solver using min-cost flow with Bellman-Ford algorithm.
    
    This solver constructs a flow network and uses the min-cost flow algorithm
    to find the optimal pairing solution.
    
    Attributes:
    -----------
    grid: Grid
        The grid instance.
    pairs: list
        Selected pairs in the solution.
    graph: Graph
        The flow network used for min-cost flow.
    source: str
        Source node identifier.
    sink: str
        Sink node identifier.
    cost_cache: dict
        Cache for pair costs.
    forbidden_cache: dict
        Cache for forbidden cells.
    """

    def __init__(self, grid):
        """
        Initialize the Bellman-Ford solver with a grid.
        
        Parameters:
        -----------
        grid: Grid
            The input grid to solve.
        """
        super().__init__(grid)
        self.pairs = []
        self.graph = Graph()
        self.source = "S"
        self.sink = "T"
        self.cost_cache = {}
        self.forbidden_cache = {}

    def build_graph(self):
        """
        Build the flow network for the grid.
        
        Constructs a bipartite graph where:
        - Even cells connect to the source
        - Odd cells connect to the sink
        - Valid pairs form edges between even and odd cells
        """
        valid_cells = []
        even_cells = []
        odd_cells = []
        
        # Separates cells between two categories: i + j odd or even
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                if self.is_forbidden_cached(i, j):
                    continue
                    
                cell = (i, j)
                valid_cells.append(cell)
                
                if (i + j) % 2 == 0:
                    even_cells.append(cell)
                else:
                    odd_cells.append(cell)
        
        for cell in even_cells:
            self.graph.add_edge(self.source, cell, 1, 0) # Adds an edge between source and even cells
            self.add_edges_from(cell) # Adds edges between even and odd cells
            
        for cell in odd_cells:
            self.graph.add_edge(cell, self.sink, 1, 0) # Adds an edge between odd cells and sink

    # Uses cache for memorizing forbidden cells to reduce compute

    def is_forbidden_cached(self, i, j):
        """
        Check if a cell is forbidden, using cache for efficiency.
        
        Parameters:
        -----------
        i: int
            Row index
        j: int
            Column index
            
        Returns:
        --------
        bool
            True if the cell is forbidden, False otherwise
        """
        if (i, j) not in self.forbidden_cache:
            self.forbidden_cache[(i, j)] = self.grid.is_forbidden(i, j)
        return self.forbidden_cache[(i, j)]

    def add_edges_from(self, cell):
        """
        Add edges from a cell to its valid neighbors.
        
        Parameters:
        -----------
        cell: tuple
            The (i, j) coordinates of the cell
        """
        i, j = cell
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.grid.n and 0 <= nj < self.grid.m:
                neighbor = (ni, nj)
                if not self.is_forbidden_cached(ni, nj) and self.grid.test_pair(cell, neighbor):
                    cost = self.get_cost_cached((cell, neighbor))
                    self.graph.add_edge(cell, neighbor, 1, cost)


    # Uses cache for memorizing costs to reduce compute
    def get_cost_cached(self, pair):
        """
        Get the cost of a pair, using cache for efficiency.
        
        Parameters:
        -----------
        pair: tuple
            A ((i1, j1), (i2, j2)) pair
            
        Returns:
        --------
        int
            The cost of the pair
        """
        if pair not in self.cost_cache:
            self.cost_cache[pair] = self.grid.cost(pair)
        return self.cost_cache[pair]
   
    def score(self):
        """
        Compute the total score using the base implementation with caching.
        
        Returns:
        --------
        int
            The total score of the current solution
        """
        return super().score()

    def run(self):
        """
        Run the Bellman-Ford solver to find optimal pairing.
        
        Returns:
        --------
        int
            The total score of the selected pairs
        """
        # Reset graph & caches
        self.graph = Graph()
        self.cost_cache.clear()
        self.forbidden_cache.clear()
        self.pairs = []

        self.build_graph()
        _, self.pairs = self.graph.min_cost_flow(self.source, self.sink)
        return self.score()