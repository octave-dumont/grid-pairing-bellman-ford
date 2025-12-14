# Rules for the grid-pairing problem

This file defines the rules of the grid pairing optimization problem implemented in this project.

---

## 1. Grid

We consider a rectangular grid of size $n \\times m$ with:

- $n \\ge 1$ rows indexed by $i \\in \\{0, \\dots, n-1\\}$
- $m \\ge 2$ columns indexed by $j \\in \\{0, \\dots, m-1\\}$

Each cell is identified by its coordinates $(i, j)$.

Each cell $(i, j)$ has two attributes:

- a **color** $c(i, j) \\in \\{0, 1, 2, 3, 4\\}$
- an **integer value** $v(i, j) \\ge 1$ (for non‑black cells)

---

## 2. Colors

The color code is:

- $0 =$ white ($W$)
- $1 =$ red ($R$)
- $2 =$ blue ($B$)
- $3 =$ green ($G$)
- $4 =$ black ($B$) ; "forbidden cells"

> Black cells represent prohibited positions: they cannot be used in any pair and their value is not counted in the final score.

---

## 3. Valid pairs

We select **pairs of cells** under the following constraints:

### 3.1 Adjacency constraint

A pair consists of two **distinct** cells that are **orthogonally adjacent**.

Cells $(i_1, j_1)$ and $(i_2, j_2)$ may form a pair if and only if:

- either $i_1 = i_2$ and $|j_1 - j_2| = 1$ (same row, adjacent columns),  
- or $j_1 = j_2$ and $|i_1 - i_2| = 1$ (same column, adjacent rows).

There is **no wrap‑around**: first and last row/column are not adjacent.

### 3.2 Color compatibility

Let $c(i, j)$ be the color code of cell $(i, j)$.

- **Black cells ($4$)**  
  A pair **cannot** contain any black cell.  
  If $c(i, j) = 4$ for any endpoint of a potential pair, that pair is forbidden.

- **Allowed color pairings (non‑black only)**
  Valid color combinations for a pair $(c_1, c_2)$ with $c_1, c_2 \\in \\{0, 1, 2, 3\\}$ are:

  - **White** $W$ can be paired with any non‑black color:
    $(W, W),\\ (W, R),\\ (W, B),\\ (W, G)$
  - **Blue** $B$ can be paired like so:
    $(B, B),\\ (B, R),\\ (B, W)$
  - **Red** $R$ can be paired like so:
    $(R, R),\\ (R, B),\\ (R, W)$
  - **Green** $G$ can be paired **only** with white:
    $(G, G),\\ (G, W)$

Order does not matter: if $(c_1, c_2)$ is allowed, then $(c_2, c_1)$ is also allowed.

### 3.3 Uniqueness constraint

Each cell can be used in **at most one pair**.

If $\\mathcal{P}$ is the set of selected pairs and $(i, j)$ is a cell, then $(i, j)$ appears in at most one element of $\\mathcal{P}$.

---

## 4. Objective (score)

Given a **valid list of pairs** $\\mathcal{P}$ (satisfying all constraints above), the **score** is defined as follows.

1. For each pair $((i_1, j_1), (i_2, j_2)) \\in \\mathcal{P}$, we add:
   $\\bigl|\\,v(i_1, j_1) - v(i_2, j_2)\\,\\bigr|$
   to the score.

2. For each cell $(i, j)$ that:
   - is **not** in any pair in $\\mathcal{P}$, and  
   - is **not black** $\\bigl(c(i, j) \\ne 4\\bigr)$,

   we add $v(i, j)$ to the score.

The total score is therefore:

$$\\text{score}(\\mathcal{P})
= \\sum_{((i_1,j_1),(i_2,j_2)) \\in\\mathcal{P}} \\bigl|v(i_1,j_1) - v(i_2,j_2)\\bigr|
\\;+\\;
\\sum_{\\substack{(i,j)\\ \\text{unpaired} \\\\ c(i,j) \\ne 4}} v(i,j).$$

_**Goal:** Find a valid set of pairs_ $\\mathcal{P}$ _that **minimises**_ $\\text{score}(\\mathcal{P})$.

---

## 5. Input file format

Grid instances are stored in text files named for example `gridXY.in` with the following format:

1. First line:
   ```text
   n m
   ```
   where $n$ is the number of rows and $m$ is the number of columns.

2. Next $n$ lines:
   - Each line contains $m$ integers in $\\{0,1,2,3,4\\}$, separated by spaces.  
   - These are the **colors** $c(i, j)$ for each row.

3. Optionally, the next $n$ lines:
   - Each line contains $m$ positive integers, separated by spaces.  
   - These are the **values** $v(i, j)$ for each row.

4. If the value lines are **absent** (the file has only $n + 1$ lines):
   - All non‑black cells are assumed to have value $1$.

Example ($2 \\times 3$ grid with explicit values):

```text
2 3
0 0 0
0 0 0
5 8 4
11 1 3
```

Example ($2 \\times 3$ grid with colors only, all values implicitly set to $1$):

```text
2 3
0 4 3
2 1 0
```

---

This project implements:

- a `Grid` class that encodes this structure and rules;
- solvers that produce valid pair sets $P$ under these rules, including an optimal solver based on min‑cost flow with Bellman–Ford.
