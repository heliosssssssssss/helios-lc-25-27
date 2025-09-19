import os
import time

class Solution():
    def __init__(self):
        self.order_of_logic()

    def order_of_logic(self):
        self.initalize()

    def initalize(self):
        rain_check = str(input("hey is it raining? (yes/no) : ")).lower()

        match rain_check:
            case "yes" | "y":
                wind_check = str(input("okay, is it windy? (yes/no) : ")).lower()
                match wind_check: # NESTED 
                    case "yes" | "y":
                        print("it is too windy for an umbrella")
                    case "no" | "n":
                        print("take an umbrella")
                        
            case "no" | "n":
                print("enjoy your day, mate")
            case _: 
                print("[ALERT] : A error has been detected, please retry")
                time.sleep(2)
                os.system("cls")
                self.initalize()

# was hgoin to do lambda but no
Solution()