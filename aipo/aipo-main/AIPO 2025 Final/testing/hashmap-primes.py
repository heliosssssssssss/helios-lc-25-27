def gen_primes(n):

    primes = {i: True for i in range(2, n + 1)}
    for p in range(2, int(n ** 0.5) + 1):
        if primes[p]:
            for multiple in range(p * p, n + 1, p):
                primes[multiple] = False

    return primes