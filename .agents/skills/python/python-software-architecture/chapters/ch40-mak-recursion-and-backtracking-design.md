# Chapter 40: Designing Solutions with Recursion and Backtracking

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 5: Additional Design Techniques (Chapter 15)

## Core Idea
Recursion solves complex problems by breaking them into self-similar smaller subproblems with well-defined base cases; backtracking systematically explores candidate solutions within a combinatorial state space, immediately abandoning invalid candidates (pruning) to find valid configurations.

## Frameworks Introduced
- **The Recursive Problem Decomposition Framework**:
  - When to use: Problems with hierarchical, nested, or self-similar structures (trees, divide-and-conquer, expression parsing).
  - How:
    1. **Base Case(s)**: Identify the simplest terminating conditions where the answer is known without further calls.
    2. **Recursive Step**: Reduce the problem to one or more strictly smaller instances of the identical problem.
    3. **Combination**: Combine subproblem results into the overall solution.
- **The Backtracking Exploration Template**:
  - When to use: Constraint satisfaction problems, puzzle solving (Sudoku, N-Queens), and combinatorial search (permutations, subsets).
  - How:
    1. Check if current state is a valid complete solution.
    2. Iterate over all candidate next choices.
    3. If choice is valid under constraints: Apply choice -> Recurse -> Undo choice (Backtrack).

## Key Concepts
- **Base Case**: The condition under which a recursive function returns directly without making further recursive calls.
- **Call Stack**: The runtime memory stack tracking active function frames; deep recursion risks `RecursionError` in Python.
- **Pruning (Branch Pruning)**: Discarding branches of the search tree that are mathematically guaranteed not to lead to a valid solution.
- **Constraint Satisfaction Problem (CSP)**: A problem defined by a set of variables that must be assigned values satisfying specific constraints.

## Mental Models
- **Backtracking as Navigating a Maze with Breadcrumbs**: You walk forward along a path. If you hit a dead end (constraint violated), you retrace your steps to the last intersection (undo choice) and try the next corridor.
- **Base Cases Are Emergency Brakes**: A recursive function without a rock-solid base case is a car driving toward a cliff with no brakes.

## Anti-patterns
- **Missing or Flawed Base Cases**: Failing to account for edge conditions, triggering `RecursionError: maximum recursion depth exceeded`.
- **Forgetting to Undo State in Backtracking**: Mutating shared state during forward search but failing to revert it upon returning, corrupting subsequent search paths.
- **Exhaustive Search Without Pruning**: Searching billions of invalid branches that could have been eliminated with a simple initial constraint check.

## Code Examples

```python
from typing import List, Optional

# Backtracking Template: Solving N-Queens
def solve_n_queens(n: int) -> List[List[str]]:
    solutions = []
    board = [["."] * n for _ in range(n)]
    cols = set()
    pos_diag = set()  # (r + c)
    neg_diag = set()  # (r - c)

    def backtrack(row: int):
        # 1. Base Case: All queens placed!
        if row == n:
            solutions.append(["".join(r) for r in board])
            return

        # 2. Iterate candidates
        for col in range(n):
            # Prune invalid branches immediately
            if col in cols or (row + col) in pos_diag or (row - col) in neg_diag:
                continue

            # Apply choice
            cols.add(col)
            pos_diag.add(row + col)
            neg_diag.add(row - col)
            board[row][col] = "Q"

            # Recurse
            backtrack(row + 1)

            # Undo choice (Backtrack)
            cols.remove(col)
            pos_diag.remove(row + col)
            neg_diag.remove(row - col)
            board[row][col] = "."

    backtrack(0)
    return solutions
```
- **What it demonstrates**: Standard backtracking template with branch pruning (sets for diagonals and columns) and state undoing.

## Reference Tables

| Algorithm Type | Exploration Strategy | Memory Mechanism | Best Suited For |
|---|---|---|---|
| **Divide & Conquer**| Splits problem in halves | Call stack | Sorting (Merge/Quick), Binary Search |
| **Pure Recursion** | Walks nested structures | Call stack | Tree traversal, AST evaluation |
| **Backtracking** | Explores with rollback | State + Call stack | Puzzles, CSP, Knapsack, N-Queens |
| **Dynamic Programming**| Caches overlapping subproblems| Lookup table / Memo | Shortest path, Fibonacci, Edit distance |

## Worked Example
Tail-call limitation awareness in Python:
Python does not optimize tail-call recursion (`sys.getrecursionlimit()` defaults to 1000).
When designing recursive algorithms for deep structures:
1. Increase limit cautiously: `sys.setrecursionlimit(5000)` OR
2. Refactor to an explicit loop with an in-memory stack (trampoline pattern) for production safety:
```python
def iterative_walk(root):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node.value
        stack.extend(reversed(node.children))
```

## Key Takeaways
1. Every recursive function must have at least one explicit base case that stops recursion.
2. Backtracking follows the formula: Check solution -> Validate candidate -> Apply -> Recurse -> Undo.
3. Prune invalid branches as early as possible to prevent combinatorial explosion.
4. Mind Python's default recursion depth limit for deeply nested data structures.

## Connects To
- **Ch 36**: Traversing tree structures with recursion and iterators.
- **Ch 39**: Composite tree structures naturally processed via recursive methods.
- **Ch 27**: Iterative problem solving.
