import random
N, M = 4, 5
grid = [
    [1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1],
    [2, 3, -2, 3, 10],
    [-100, -5, -1, -1, -1]
]

def Solution(n, m, grid):
    row = n 
    col = m 
    grid = grid 

    added_rows = []
    t_value = 0

    for _row in grid:
        for _number in _row:
            t_value = int(t_value) + int(_number)

        added_rows.append(t_value)
        t_value = 0


    return added_rows
        

def solution(n, m, grid):
    return [sum(row) for row in grid]

def generate_test_cases():
    test_cases = []

    # Case 1: Minimum size grid (1x1)
    test_cases.append((1, 1, [[random.randint(-1000, 1000)]]))

    # Case 2: Small grid with positive numbers
    test_cases.append((2, 2, [[1, 2], [3, 4]]))

    # Case 3: Small grid with negative numbers
    test_cases.append((2, 2, [[-1, -2], [-3, -4]]))

    # Case 4: Mixed values
    test_cases.append((3, 3, [[-1, 2, -3], [4, -5, 6], [-7, 8, -9]]))

    # Case 5: Maximum values (-1000, 1000)
    test_cases.append((4, 4, [[random.choice([-1000, 1000]) for _ in range(4)] for _ in range(4)]))

    # Case 6: Large but feasible grid (e.g., 100x100)
    test_cases.append((100, 100, [[random.randint(-1000, 1000) for _ in range(100)] for _ in range(100)]))

    # Case 7-100: Randomly generated cases
    for _ in range(94):
        n = random.randint(1, 500)  # Keeping n and m reasonable for execution
        m = random.randint(1, 500)
        grid = [[random.randint(-1000, 1000) for _ in range(m)] for _ in range(n)]
        test_cases.append((n, m, grid))

    return test_cases

def test_solution():
    test_cases = generate_test_cases()
    for i, (n, m, grid) in enumerate(test_cases):
        result = solution(n, m, grid)
        print(f"Test Case {i+1}: PASSED") if result == [sum(row) for row in grid] else print(f"Test Case {i+1}: FAILED")

# Run test cases
test_solution()
