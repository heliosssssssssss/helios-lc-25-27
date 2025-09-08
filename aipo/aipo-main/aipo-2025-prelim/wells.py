#!/usr/bin/env python3
import sys,collections

def solve():
    import sys,collections
    data = sys.stdin.read().splitlines()
    if not data:
        return
    # Remove empty lines and get tokens.
    lines = [line.rstrip("\n") for line in data if line.strip() != ""]
    if not lines:
        return
    try:
        t = int(lines[0].strip())
    except:
        return
    index = 1
    out_lines = []
    
    # --- Part 1. Physical reachability BFS ---
    # Given the two–wall grid (with H rows, row 0 = bottom, row H-1 = top)
    # and jump size J, check whether there is any sequence of (up,down,jump)
    # moves that gets Wendy “out” (i.e. to a brick position with height >= H).
    def can_reach_top_physically(H, J, grid):
        q = collections.deque()
        visited = [[False, False] for _ in range(H)]
        # starting at (0,0) [bottom left]
        q.append((0,0))
        visited[0][0] = True
        while q:
            h, wall = q.popleft()
            # Up:
            nh = h + 1
            if nh >= H:
                return True
            if grid[nh][wall] == '.':
                if not visited[nh][wall]:
                    visited[nh][wall] = True
                    q.append((nh, wall))
            # Down:
            if h > 0:
                nh = h - 1
                if grid[nh][wall] == '.':
                    if not visited[nh][wall]:
                        visited[nh][wall] = True
                        q.append((nh, wall))
            # Jump:
            nh = h + J
            nwall = 1 - wall
            if nh >= H:
                return True
            if nh < H and grid[nh][nwall] == '.':
                if not visited[nh][nwall]:
                    visited[nh][nwall] = True
                    q.append((nh, nwall))
        return False

    # --- Part 2. Timed (race) BFS ---
    # We “layer” the state by the number r of moves Wendy has already made.
    # (Remember: in our model we “pretend” that initially Wally is below the well.)
    # Thus when making move number r+1 (r starting at 0), landing on a brick with height r is forbidden.
    # If a move would yield a height >= H then Wendy escapes (and wins immediately).
    def can_win(H, J, grid):
        M = (H + 1) // 2   # maximum moves = ceil(H/2)
        current = set()
        # starting state (0,0, left) – we only need to store (h,wall) because r is the layer index.
        current.add((0, 0))
        for r in range(M):
            next_layer = set()
            for (h, wall) in current:
                # Move 1: Climb Up -> (h+1, same wall)
                nh = h + 1
                nwall = wall
                if nh >= H:
                    return True
                if nh == r:
                    pass  # forbidden: would mean that when Wally moves next, he catches her.
                else:
                    if grid[nh][nwall] == '.':
                        next_layer.add((nh, nwall))
                # Move 2: Climb Down -> (h-1, same wall) if possible.
                if h > 0:
                    nh = h - 1
                    nwall = wall
                    if nh >= H:
                        return True
                    if nh == r:
                        pass
                    else:
                        if grid[nh][nwall] == '.':
                            next_layer.add((nh, nwall))
                # Move 3: Jump -> (h+J, opposite wall)
                nh = h + J
                nwall = 1 - wall
                if nh >= H:
                    return True
                if nh == r:
                    pass
                else:
                    if grid[nh][nwall] == '.':
                        next_layer.add((nh, nwall))
            if not next_layer:
                return False
            current = next_layer
        return False

    # Process each test case.
    for _ in range(t):
        if index >= len(lines):
            break
        parts = lines[index].split()
        index += 1
        if len(parts) < 2:
            continue
        try:
            H = int(parts[0])
            J = int(parts[1])
        except:
            continue
        # Next H lines describe the well.
        # The problem states that the bottom brick is the last line.
        raw = []
        for i in range(H):
            if index >= len(lines):
                break
            line = lines[index]
            index += 1
            raw.append(line.rstrip("\n"))
        # Reverse so that grid[0] is the bottom brick.
        grid = raw[::-1]
        # grid is a list of H strings (each of length 2); grid[r][0] is the left–wall brick at height r.
        
        # (A) Physical reachability check.
        if not can_reach_top_physically(H, J, grid):
            out_lines.append("FORFEIT")
        else:
            # (B) Timed “race” DP/BFS.
            if can_win(H, J, grid):
                out_lines.append("WENDY")
            else:
                out_lines.append("WALLY")
    sys.stdout.write("\n".join(out_lines))

if __name__ == '__main__':
    solve()
