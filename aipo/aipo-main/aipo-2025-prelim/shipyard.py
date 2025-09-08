MODULO = 20242024

def count_transport_ways(n, m):
    # Edge case: No containers or invalid input
    if n <= 0 or m <= 0:
        return 0

    # Edge case: Lorry can carry all containers in one trip
    if m >= n:
        return 1

    # Edge case: Only one container per trip
    if m == 1:
        return 1

    # Dynamic programming with a circular buffer
    dp = [0] * (m + 1)  # Use a circular buffer to save space
    dp[0] = 1  # Base case: 1 way to transport 0 containers
    running_sum = 1  # Sliding window sum

    for i in range(1, n + 1):
        dp_index = i % (m + 1)
        if i > m:
            running_sum = (running_sum - dp[(i - m - 1) % (m + 1)] + MODULO) % MODULO
        dp[dp_index] = running_sum
        running_sum = (running_sum + dp[dp_index]) % MODULO

    return dp[n % (m + 1)]

# Input handling
n, m = map(int, input().split())
print(count_transport_ways(n, m))
