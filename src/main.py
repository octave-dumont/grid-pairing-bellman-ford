import numpy as np
import time
from gridpairing.grid import Grid
from gridpairing.solvers import SolverNaive, SolverBellmanFord
import pandas as pd

def test_grid_methods(grid,plot=False):
    """
    Tests and displays:
    - Grid representation
    - The all_pairs() method in order to return the valid pairs in the grid
    - Visualization of the grid using the plot() method
    
    Parameters:
    ----------
    grid : Grid
        The grid object to test
    plot : bool
        If True, displays the grid with pairs (default: False)
    """
    print("\n==================== Testing Grid methods ====================")
   
    print("Grid representation:\n", grid)
    print("\nTesting all_pairs() method:")
    pairs = grid.all_pairs()

    number_pairs_to_print = 5

    if pairs:
        print(f"Number of valid pairs: {len(pairs)}")
        print(f"First {number_pairs_to_print} valid pairs: {pairs[:min(number_pairs_to_print, len(pairs))]}")
    else:
        print("No valid pair found")

    # Disable this plot testing fo 200*100 grids
    if plot:
        grid.plot()

def test_solver(solver, solver_name):
    """
    Tests a solver's performance on a grid problem.
    
    Reports performance metrics including:
      - Final score
      - Number of pairs found
      - Execution time
    
    Parameters:
    ----------
    solver : Solver
        The solver object to test
    solver_name : str
        Name of the solver for display purposes
        
    Returns:
    -------
    float
        The final score achieved by the solver
    """
    print(f"\n==================== Running {solver_name} ====================")

    # Calculating the time taken by the solver
    start_time = time.time()
    score = solver.run()
    execution_time = time.time() - start_time 

    print(f"\n{solver_name} completed!")
    print(f"Final score : {score}")
    print(f"Number of pairs found : {len(solver.pairs)}")
    print(f"Runtime: {execution_time:.4f}s")
    return score

def run_tests_on_grids(grids_to_test,plot=False):
    """
    Runs a complete test suite on a given list of grid numbers.
    
    Parameters:
    ----------
    grids_to_test : list of str
        List of grid file numbers to test (ex: ["23"] for "input/grid23.in")
    plot : bool
        If True, displays the grid with selected pairs (default: False)
    """
    for grid_number in grids_to_test:
        print(f"\n==================== Loading Grid from input/grid{grid_number}.in ====================")
        try:
            grid = Grid.grid_from_file("input/grid"+grid_number+".in", read_values=True)
            test_grid_methods(grid)

            # Testing SolverNaive
            naive_solver = SolverNaive(grid)
            naive_score = test_solver(naive_solver, "SolverNaive")

            # Saving SolverNaive solutions
            data = [(i1, j1, i2, j2) for (i1, j1), (i2, j2) in naive_solver.pairs]
            df = pd.DataFrame(data, columns=["i1", "j1", "i2", "j2"])
            df.to_csv("examples_solving/Solved_naive_grid" + grid_number + ".csv", index=False)

            # Disable the pairings plot for 200*100 grids
            if plot:
                grid.plot(naive_solver.pairs)

            # Testing SolverBellmanFord like above
            BF_solver = SolverBellmanFord(grid)
            BF_score = test_solver(BF_solver, "SolverBellmanFord")

            data2 = [(i1, j1, i2, j2) for (i1, j1), (i2, j2) in BF_solver.pairs]
            df2 = pd.DataFrame(data2, columns=["i1", "j1", "i2", "j2"])

            df2.to_csv("examples_solving/Solved_bellman_ford_grid" + grid_number + ".csv", index=False)

            # Disable the pairings plot for 200*100 grids
            if plot:
                grid.plot(BF_solver.pairs)

            # Scores comparison
            print(f"\n\nComparison: \nSolverNaive Score = {naive_score}\nSolverBellmanFord Score = {BF_score}")
            print(f"\n{'SolverNaive' if naive_score < BF_score else 'SolverBellmanFord'} got the best score.")

        except Exception as e:
            print(f"Error loading input/grid{grid_number}.in: {e}")

if __name__ == "__main__":
    # List of the grids to test
    test_files = ["01"]

    # Running tests
    run_tests_on_grids(test_files)