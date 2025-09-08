# inputs -> n = number amount (we ignore), message = dates

## the actual process :
## get substrings that may represent DDMMYYYY, then check validity

# ! EDGE CASES TO REMEMBER ! 
# (if input is empty? if input only has 1 element? if input is very large? is input the wrong type?)

# outputs -> final result


from datetime import datetime

def Solution(message):
    date_format = "%d-%m-%Y"

    min_date = datetime.strptime("15-02-2025", date_format)
    max_date = datetime.strptime("01-01-2028", date_format)
    
    for i in range(len(message) - 9):
        substring = message[i:i+10]
        
        try:
            date = datetime.strptime(substring, date_format)
            
            if min_date < date < max_date:
                return substring
        except ValueError:
            continue
    
    return None

N = int(input())
message = input().strip()

valid_date = Solution(message)
print(valid_date)