import matplotlib.pyplot as plt
import matplotlib.patches as patches
"""
This is the grid module. It contains the Grid class and its associated methods.
"""

class Grid():
    """
    A class representing the grid. 

    Attributes: 
    -----------
    n: int
        Number of lines in the grid
    m: int
        Number of columns in the grid
    color: list[list[int]]
        The color of each grid cell: value[i][j] is the value in the cell (i, j), i.e., in the i-th line and j-th column. 
        Note: lines are numbered 0..n-1 and columns are numbered 0..m-1.
    value: list[list[int]]
        The value of each grid cell: value[i][j] is the value in the cell (i, j), i.e., in the i-th line and j-th column. 
        Note: lines are numbered 0..n-1 and columns are numbered 0..m-1.
    colors_list: list[char]
        The mapping between the value of self.color[i][j] and the corresponding color
    """
    

    def __init__(self, n, m, color=None, value=[]):
        """
        Initializes the grid.

        Parameters: 
        -----------
        n: int
            Number of lines in the grid
        m: int
            Number of columns in the grid
        color: list[list[int]]
            The grid cells colors. Default is empty (then the grid is created with each cell having color 0, i.e., white).
        value: list[list[int]]
            The grid cells values. Default is empty (then the grid is created with each cell having value 1).
        
        The object created has an attribute colors_list: list[char], which is the mapping between the value of self.color[i][j] and the corresponding color
        """
        self.n = n
        self.m = m
        if not color:
            color = [[0 for j in range(m)] for i in range(n)]            
        self.color = color
        if not value:
            value = [[1 for j in range(m)] for i in range(n)]            
        self.value = value
        self.colors_list = ['w', 'r', 'b', 'g', 'k']

    def __str__(self): 
        """
        Prints the grid as text.
        """
        output = f"The grid is {self.n} x {self.m}. It has the following colors:\n"
        for i in range(self.n): 
            output += f"{[self.colors_list[self.color[i][j]] for j in range(self.m)]}\n"
        output += f"and the following values:\n"
        for i in range(self.n): 
            output += f"{self.value[i]}\n"
        return output

    def __repr__(self): 
        """
        Returns a representation of the grid with number of rows and columns.
        """
        return f"<grid.Grid: n={self.n}, m={self.m}>"

    def plot(self, pairs=None): 
        """
        Plots a visual representation of the grid.
        """
        fig, ax = plt.subplots()
        facecolors=["white","red","blue","green","black"]
        for i in range(self.n):
            for j in range(self.m):
                facecolor = facecolors[self.color[i][j]]
                ax.add_patch(patches.Rectangle((j, i), 1, 1, facecolor=facecolor))
                ax.text(j + 0.5, i + 0.5, str(self.value[i][j]), ha='center', va='center',color = "white" if (facecolor == "black" or facecolor == "blue") else "black")

        # Draws the selected pairs if a solver's output was given
        if pairs:
            for (x1, y1), (x2, y2) in pairs:
                plt.plot([y1 + 0.5, y2 + 0.5], [x1 + 0.5, x2 + 0.5], color="yellow",linewidth=5)
        ax.set_xlim(0, self.m)
        ax.set_ylim(0, self.n)
        plt.axis("off")
        plt.show()

    def is_forbidden(self, i, j):
        """
            Checks if the cell at position (i, j) is forbidden (i.e., black).

            Parameters:
            -----------
            i: int
                The row index of the cell.
            j: int
                The column index of the cell.

            Returns:
            --------
            bool
                True if the cell is black (forbidden), False otherwise.
            """
        return self.color[i][j] == 4
    
    def non_adjacent(self,c1,c2):
        """
            Checks if two cells are non-adjacent.

            Parameters:
            -----------
            c1: tuple[int, int]
                Coordinates of the first cell in the format (i, j).
            c2: tuple[int, int]
                Coordinates of the second cell in the format (i, j).

            Returns:
            --------
            bool
                True if the cells are non-adjacent, False otherwise.
            """
        if (c1[1]==c2[1] and abs(c1[0]-c2[0])==1) or (c1[0]==c2[0] and abs(c1[1]-c2[1])==1):
            return False
        else:
            return True
        
    def colors_forbidden(self,c1,c2):
        """
        Checks whether two cells can be paired based on their colors.

        Parameters:
        -----------
        c1: tuple[int, int]
            Coordinates of the first cell in the format (i, j).
        c2: tuple[int, int]
            Coordinates of the second cell in the format (i, j).
        Pairing rules:
        - A white cell can be paired with any other color (except black).
        - A blue cell can be paired with a blue, red, or white cell.
        - A red cell can be paired with a blue, red, or white cell.
        - A green cell can only be paired with a green cell (or white).
        - A black cell cannot be paired with any other cell.

        Returns:
        -----------
        bool
            True if the pairing is not allowed, False otherwise.
        """
        color_rules = {
        0: lambda c: False,  # White can pair with any non-black
        1: lambda c: c > 2,   # Red can pair with red, blue, or white
        2: lambda c: c > 2,   # Blue can pair with red, blue, or white
        3: lambda c: c not in {0, 3},  # Green can only pair with green or white
        4: lambda c: True    # Black is always forbidden
    }
        return color_rules[self.color[c1[0]][c1[1]]](self.color[c2[0]][c2[1]])
    
    def test_pair(self,c1,c2):
        """
            Checks if a pair of cells is valid based on the following criteria:
            - Neither cell is forbidden (i.e., black).
            - The cells are adjacent.
            - The pairing of the cells' colors is allowed based on the defined rules.

            Parameters:
            -----------
            c1: tuple[int, int]
                Coordinates of the first cell in the format (i, j).
            c2: tuple[int, int]
                Coordinates of the second cell in the format (i, j).

            Returns:
            --------
            bool
                True if the pair is valid, False otherwise.
            """
        return not(self.is_forbidden(c1[0],c1[1]) or self.is_forbidden(c2[0],c2[1]) or self.non_adjacent(c1,c2) or self.colors_forbidden(c1,c2))

    def cost(self, pair):
        """
        Returns the cost of a pair
 
        Parameters: 
        -----------
        pair: tuple[tuple[int]]
            A pair in the format ((i1, j1), (i2, j2))

        Output: 
        -----------
        cost: int
            the cost of the pair defined as the absolute value of the difference between their values
        """
        return abs(self.value[pair[0][0]][pair[0][1]]-self.value[pair[1][0]][pair[1][1]])


    def all_pairs(self):
        """
        Returns a list of all pairs of cells that can be taken together. 
        Complexity: O(n * m) since there are n*m cells and we test only the adjacent cells (2 * n * m)
        Outputs a list of tuples of tuples [(c1, c2), (c1', c2'), ...] where each cell c1 etc. is itself a tuple (i, j)
        """
        pairs = []
        for i in range(self.n):
            for j in range(self.m):
                # Tests the right and the below neighbors
                if j + 1 < self.m and self.test_pair((i, j), (i, j + 1)):
                    pairs.append(((i, j), (i, j + 1)))
                if i + 1 < self.n and self.test_pair((i, j), (i + 1, j)):
                    pairs.append(((i, j), (i + 1, j)))
        # Ensures to return only unique pairs
        return list(set(pairs))
    
    @classmethod
    def grid_from_file(cls, file_name, read_values=True): 
        """
        Creates a grid object from class Grid, initialized with the information from the file file_name.
        
        Parameters: 
        -----------
        file_name: str
            Name of the file to load. The file must be of the format: 
            - first line contains "n m" 
            - next n lines contain m integers that represent the colors of the corresponding cell
            - next n lines [optional] contain m integers that represent the values of the corresponding cell
        read_values: bool
            Indicates whether to read values after having read the colors. Requires that the file has 2n+1 lines

        Output: 
        -------
        grid: Grid
            The grid
        """
        with open(file_name, "r") as file:
            n, m = map(int, file.readline().split())
            color = [[] for i_line in range(n)]
            for i_line in range(n):
                line_color = list(map(int, file.readline().split()))
                if len(line_color) != m: 
                    raise Exception("Invalid format")
                for j in range(m):
                    if line_color[j] not in range(5):
                        raise Exception("Invalid color")
                color[i_line] = line_color

            if read_values:
                value = [[] for i_line in range(n)]
                for i_line in range(n):
                    line_value = list(map(int, file.readline().split()))
                    if len(line_value) != m: 
                        raise Exception("Invalid format")
                    value[i_line] = line_value
            else:
                value = []

            grid = Grid(n, m, color, value)
        return grid

