# Optimal Grid Pairing with Min-Cost Flow (Bellman–Ford)

Python implementation of an optimal pairing solver on 2D grids using:
- A **naive greedy solver** for quick baselines
- An **optimal min-cost flow solver** based on **successive shortest paths with Bellman–Ford**
- An **interactive Pygame UI** to play with the grid and visualize solutions

Originally developed as part of an ENSAE Paris L3 programming project about _“optimisation d’appariements sur grille”_ (_grid matching optimization_).
For the **precise problem statement, grid definition and scoring rules**, see **[RULES.md](RULES.md)**.
---

## Features

- **Grid model (`Grid`)**
  - Encodes colors, values and constraints (forbidden cells, color compatibility, adjacency)
  - Efficient generation of all valid pairs in **O(n·m)**
  - The exact rules and scoring function are documented in **[RULES.md](RULES.md)**.

- **Two solvers**
  - `SolverNaive`: greedy solver sorting all valid pairs by cost and picking non-conflicting ones
  - `SolverBellmanFord`: exact solver using **min-cost flow + Bellman–Ford** to reach the global optimum

- **Min-cost flow with Bellman–Ford**
  - Modeling the grid as a **bipartite graph** (even vs odd cells)
  - Successive shortest path algorithm with an optimized Bellman–Ford inner loop
  - Caching and reduced adjacency to keep large instances tractable

- **Interactive UI (Pygame)**
  - Select pairs and see the score evolve in real time
  - Run the optimal Bellman–Ford solver and compare its solution against your manual one

- **Experiment utilities**
  - CSV export of solutions via `pandas`
  - Simple benchmarking script to compare solvers (score, runtime, number of pairs)

---

## Project structure

```text
grid-pairing-bellman-ford/
└── src/
    ├── gridpairing/
    │   ├── __init__.py        # exposes Grid, SolverNaive, SolverBellmanFord
    │   ├── grid.py            # Grid class and grid rules
    │   ├── solvers.py         # Naive solver + Bellman–Ford min-cost flow solver
    │   └── ui_pygame.py       # Interactive Pygame UI
    ├── main.py                # Benchmark / demo script
    ├── tests/                 # Unit tests
    │   ├── test_grid_from_file.py
    │   └── test_valid_pairs.py
    ├── input/                 # Grid instances used by the project
    │   ├── grid00.in
    │   ├── grid01.in
    │   └── ...
    └── examples_solving/      # (created by main.py) CSV solutions
```

> **Note**: `main.py` and the UI read grids as `input/gridXX.in` relative to the `src` directory.

---

## Installation

```bash
git clone https://github.com/octave-dumont/grid-pairing-bellman-ford.git
cd grid-pairing-bellman-ford

# (Optional) create a virtualenv
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install runtime dependencies
pip install pygame pandas matplotlib
```

No packaging step is strictly required: the project is meant to be run directly from `src`.

---

## Usage

### 1. Run the benchmark script

This script loads a few grids from `src/input/`, runs both solvers, compares scores and writes CSV files in `src/examples_solving/`.

```bash
cd src
python main.py
```

You can change the tested grids inside `main.py` by editing:

```python
test_files = ["XX"]
```

---

### 2. Run the interactive Pygame UI

```bash
cd src
python -m gridpairing.ui_pygame
```

The UI lets you:

- click cells to create/delete valid pairs  
- see your current score  
- press **Space** or use the button to run the optimal Bellman–Ford solver  
  and compare your manual solution to the optimum

To use another grid file, change the path in `gridpairing/ui_pygame.py` where `Grid.grid_from_file(...)` is called (it will still be relative to `src`, e.g. `"input/grid15.in"`).

---

## Running tests

Unit tests live in `src/tests/` and use the `gridpairing` package.

From the repository root:

```bash
cd src
python -m unittest discover -s tests
```

This will:

- check that `Grid.grid_from_file()` correctly loads example grids
- verify that all pairs returned by `Grid.all_pairs()` are valid and respect the constraints

---

## Using the code as a mini-library

If you want to use the solvers from a notebook or another script (also launched from `src`):

```python
from gridpairing import Grid, SolverBellmanFord, SolverNaive

grid = Grid.grid_from_file("input/grid01.in", read_values=True)
solver = SolverBellmanFord(grid)
score = solver.run()

print("Best score:", score)
print("Number of pairs:", len(solver.pairs))
```

This relies on the `__init__.py` that exposes the public API of the `gridpairing` package.

---

## Acknowledgements

This project was originally implemented as an ENSAE Paris L3 programming project on grid pairing optimization, and then refactored into a small, self-contained Python package with an interactive UI.
