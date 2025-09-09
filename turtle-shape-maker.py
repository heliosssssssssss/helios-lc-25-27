from turtle import *
import math
from time import sleep 

def solution_1(count): # question_4
    for x in range(count):
        forward(50)
        left(90)
        forward(100)
        right(90)
        
def solution_2(): # square
    corners = 4
    for x in range(corners):
        forward(50)
        left(360 / corners)
        
def solution_3(): # 50x100 red rectangle
    color("red")
    
    forward(50)
    left(90)
    forward(100)
    left(90)
    forward(50)
    left(90)
    forward(100)
    
    
def solution_3(): # red T w hidden pen
    upper_length = 100
    
    color("red")
    forward(upper_length)
    up()
    backward(upper_length / 2)
    down()
    right(90)
    forward(100)
    hideturtle()
    

class ShapeGenerator:
    
    def handle_menu():
        print("""

        [Customized Shape Generator]

        [1] : Make a shape
        [2] : Random shape (unstable)

""")
        
        option = input("Please select your option [1-2] : ")
        ShapeGenerator.handle_input(x = int(option))
        
    def handle_input(x : int):
        if x < 1 or x > 2:
            print("Invalid option, please retry again")
            sleep(3)
            ShapeGenerator.handle_menu()
        else:
            if x == 1: # [1] - custom
                _length = input("Input your length : ")
                _corners = input("Input how many corners you want : ")
                _color = input("Input what color you want : ")
                ShapeGenerator.generate_shape(isRandom = False, length = int(_length), corners = int(_corners), colour = _color)
            if x == 2: # [2] - random
               # ShapeGenerator.generate_shape(isRandom = True, 0, 0, " ")
               pass
            
    def generate_shape(isRandom : bool, length : int, corners : int, colour : str):
        if isRandom:
            deg = 360
            length = math.random(10, 200)
            corners = math.random(4, 360)
            
            for _c in range(corners):
                forward(length)
                left(deg / corners)
                
            return
        
        print(f"""

        [Custom Shape Generation]
        
    -> Length : {length}
    -> Corners : {corners}
    -> Color : {colour}
    
        Generating... (window may not open by default)

""")
        
        deg = 360
        for _c in range(corners):
            color(colour)
            forward(length)
            left(deg / corners)
        
        
        
ShapeGenerator.handle_menu()       
