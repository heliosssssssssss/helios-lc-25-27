from itertools import permutations

def Solution(a, n):
    scenario = int(a) 
    digits = n
    prime_map = gen_primes(100000)

    prime_count = 0

    if a == 0: 
        combos = digit_switches(n)
        for p_digits in combos:
            if prime_map[int(p_digits)] == True: 
                prime_count = prime_count + 1

        return prime_count
    else: # (a == 1) - cool_prime check
        combos = digit_switches(n)
        total_combos = len(combos)
        current_primes = 0
        
        for p_digits in combos: 
            if prime_map[int(p_digits)] == True:
                current_primes = current_primes + 1

        if current_primes == total_combos:
            print(1)
        else:
            print(0)


def gen_primes(n):

    primes = {i: True for i in range(2, n + 1)}
    for p in range(2, int(n ** 0.5) + 1):
        if primes[p]:
            for multiple in range(p * p, n + 1, p):
                primes[multiple] = False

    return primes

def digit_switches(d): 
    digit = str(d)
    combinations = []

    possibles = permutations(digit)

    for digits in possibles:
        new_value = ""
        for x in digits: 
            new_value = new_value + x
        
        if new_value in combinations:
            break
        else:
            combinations.append(new_value)

    return combinations
