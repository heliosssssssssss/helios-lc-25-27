# formula 
# f(n) = f(n-1) + f(n-2)

mod = 1000000007

def f(n):
    a, b = 0, 1

    if n == 0:
        return 0
    
    if n == 1:
        return b
    else:
        for i in range(1, n):
            c = a + b
            a = b 
            b = c 
        return b


print(f(50 % mod))