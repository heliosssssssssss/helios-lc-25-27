def solution():
    rows = 9
    cols = 9

    for row in range(rows):
        if row == 0 or row == rows - 1:
           print("*********")
        else:
           line = ""
           for col in range(cols):
                if (
                    col == 0 # left wall check
                    or col == cols - 1 # right wall check 
                    or col == row # x=y (diagnal) check
                    or col + row == rows - 1 # opposite of above
                    ):
                    line += "*"
                else:
                    line += " "
                
           print(line)

solution()