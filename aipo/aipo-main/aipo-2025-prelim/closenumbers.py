def close_num(n):
    n_str = str(n)
    num_digits = len(n_str)
    close_numbers = 0 

    for i in range(num_digits): 
        current_digit = int(n_str[i])

        for x in [-1, 1]: 
            new_digit = current_digit + x 
            if 0 <= new_digit <= 9: 
                new_number = n_str[:i] + str(new_digit) + n_str[i+1:]

                if len(new_number) == num_digits and not (new_number[0] == '0' and len(new_number) > 1):
                    close_numbers +=1 

            
    return close_numbers


print(close_num(n = input()))