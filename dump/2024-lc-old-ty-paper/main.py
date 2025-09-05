import random 
from random import randint

# d-check (4)

total = 0
item_list = []
item_prices = []

print("Welcome to my shop")

to_stop = False

def addItem(item, price):

    item_list.append(item)
    item_prices.append(price)

def getTotal(): 
    current_value = 0 
    for x in item_prices:
        current_value += x

    total = current_value

    return total

def returnData(): 
    print(f"Your items are: {item_list}")
    print(f"The prices are: {item_prices}")
    print(f"Grand total $ {getTotal()}")
    print(f"Your random item to be checked: {randomCheck()}")
    print(f"The most expensive item is: {getExpensive()}")
    print(f"The cheapest item is: {getCheapest()}")

def randomCheck(): 
    random_number = randint(0, len(item_list))
    checkable = item_list[random_number]

    return checkable

def getCheapest():
    current_low = min(item_prices)

    position = item_prices.index(current_low)
    e_item = item_list[position]

    return e_item

def getExpensive():
    current_high = 0 

    for x in item_prices: 
        if x > current_high: 
            current_high = x

    position = item_prices.index(current_high)
    e_item = item_list[position]

    return e_item

def askQuestion():

    global to_stop

    temp_item = input("Please enter the item: ")

    if temp_item == "Stop": 
        to_stop = True 
        returnData()
    else:
        temp_price = input("Please enter the price of the item: ")

            
    if to_stop == False:
        addItem(item = temp_item, price = float(temp_price))
    
        print(f"The current total is ${getTotal()}")

        askQuestion()


askQuestion()