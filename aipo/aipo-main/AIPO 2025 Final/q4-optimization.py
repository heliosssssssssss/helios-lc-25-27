# inputs -> first line c = given games that follow in 
# that it will create [next line: a of n = amount of games in game i], followed by a line containg 
# the numbers of c printed out for i

## the actual process :
##
##

# ! EDGE CASES TO REMEMBER ! 
# (if input is empty? if input only has 1 element? if input is very large? is input the wrong type?)

# outputs -> 

import math, random


def is_prime(n):
    """Miller-Rabin test for n."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in (2, 3, 5, 7, 11):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def pollard_rho(n):
    """Pollard-Rho factorization."""
    if n % 2 == 0:
        return 2
    x = random.randrange(2, n - 1)
    y = x
    c = random.randrange(1, n - 1)
    d = 1
    while d == 1:
        x = (x * x + c) % n
        y = (y * y + c) % n
        y = (y * y + c) % n
        d = math.gcd(abs(x - y), n)
        if d == n:
            return pollard_rho(n)
    return d

def factorize(n):
    """Return prime factors of n as a dict {prime: exponent}."""
    if n == 1:
        return {}
    if is_prime(n):
        return {n: 1}
    factor = pollard_rho(n)
    f1 = factorize(factor)
    f2 = factorize(n // factor)
    res = {}
    for p, exp in f1.items():
        res[p] = res.get(p, 0) + exp
    for p, exp in f2.items():
        res[p] = res.get(p, 0) + exp
    return res

def get_divisors(n):
    """Return all divisors of n."""
    facs = factorize(n)
    divisors = [1]
    for p, exp in facs.items():
        new_divs = []
        for d in divisors:
            for e in range(exp + 1):
                new_divs.append(d * (p ** e))
        divisors = new_divs
    return divisors

def try_pattern(cards, first_divisible):
    n = len(cards)
    P, Q = [], []
    for i, card in enumerate(cards):
        required = 1 if (i % 2 == 0 and first_divisible) or (i % 2 == 1 and not first_divisible) else 0
        if required == 1:
            P.append(card)
        else:
            Q.append(card)
    if n > 1 and (not P or not Q):
        return None
    g = P[0]
    for num in P[1:]:
        g = math.gcd(g, num)
    divs = get_divisors(g)
    divs.sort(reverse=True)
    for d in divs:
        if Q and d == 1:
            continue
        valid = True
        for num in Q:
            if num % d == 0:
                valid = False
                break
        if valid:
            return d
    return None

def solve_game(cards):
    n = len(cards)
    if n == 1:
        return cards[0]
    candidate = try_pattern(cards, True)
    if candidate is not None:
        return candidate
    candidate = try_pattern(cards, False)
    if candidate is not None:
        return candidate
    return "UNWINNABLE"

def Solution():
    T = int(input().strip())
    results = []
    for _ in range(T):
        n = int(input().strip())
        cards = list(map(int, input().strip().split()))
        ans = solve_game(cards)
        results.append(ans)
    print("\n".join(map(str, results)))


Solution()
