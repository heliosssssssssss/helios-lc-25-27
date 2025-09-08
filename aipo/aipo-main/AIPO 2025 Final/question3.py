# inputs -> AMOUNT OF TC, TC[STOCK, REQUIRED]

## the actual process :
## loop through each testr case and get the required and stock for both
## perform greedy rd

# version 2 (fix):
# if stock < sum check passed, it is almost certian n = 2 will result as YES therefor return 
# covered uncertian edge cases

# ! EDGE CASES TO REMEMBER ! 
# (if input is empty? if input only has 1 element? if input is very large? is input the wrong type?)

# outputs ->  YES = IF IS POSSIBLE TO MEET OR EXCEED REQUIRED, OTHERWISE NO

def get_inputs():
    t = int(input())
    test_cases = []

    for _ in range(t):
        supply_types = int(input())
        stock = list(map(int, input().split()))
        required = list(map(int, input().split()))
        test_cases.append((supply_types, stock, required))

    Solution(t, test_cases)

def Solution(t, test_cases):
    for test_case in test_cases:
        n = test_case[0]
        stock = test_case[1]
        required = test_case[2]

        if sum(stock) < sum(required):
            print("NO")
            continue

        if n == 2:
            print("YES")
            continue

        diff = sum(stock) - sum(required)
        K_max = diff // (n - 2)

        possible = True
        for i in range(n):
            if stock[i] + K_max < required[i]:
                possible = False
                break

        count_zeros = sum(1 for i in range(n) if stock[i] == 0 and required[i] > 0)
        if count_zeros >= 2:
            possible = False

        print("YES" if possible else "NO")


get_inputs()