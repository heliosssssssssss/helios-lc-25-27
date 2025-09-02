## Q10

def conversion(kg : int):
    answer = kg * 2.204
    return answer

#to_convert = float(input("enter how much kg: "))
#print(f"Your {to_convert} => {conversion(to_convert)} pounds")

## Q11

def solution(num1 : int, num2 : int):
    
    if ( # LIMIT BOUNDARY 
        
        num1 > 100 # (101+)
        or num1 < 1 # -1 check
        or num2 > 10 # 11+
        or num2 < 1 # -1 check
        ):
        
        print("[error] : please retry again (OUT_OF_BOUNDS)")
        return
    
    limit = round((num1 / num2))
    remainder = (num1 % num2)
    
    print(f"Your number: {_num2} goes into {_num1}, {limit} times with a remainder of {remainder}")

_num1 = int(input("enter a number (1-100) : "))
_num2 = int(input("enter a second number (1-10) : "))

solution(_num1, _num2)
    

