
def findEarthquake(sequence):
    n = len(sequence)
    max_duration = 0
    count_ones = 0  
    leading_zeros = 0  

    i = 0
    while i < n:
        if sequence[i] == "0":
            if count_ones == 0:
                leading_zeros += 1  
            else:
                trailing_zeros = 0
                while i < n and sequence[i] == "0":
                    trailing_zeros += 1
                    i += 1

                if leading_zeros >= 2 and trailing_zeros >= 2:
                    max_duration = max(max_duration, count_ones)

                count_ones = 0
                leading_zeros = trailing_zeros
                continue
        else:
            count_ones += 1

        i += 1

    return max_duration

n = int(input().strip())
sequence = input().strip().replace(" ", "")

print(findEarthquake(sequence))
