class Solution:

    def __init__(self):

        self.date = ""
        self.actual_year = 0
        self.weekdays = {
            0 : "Sat",
            1 : "Sun",
            2 : "Mon",
            3 : "Tue",
            4 : "Wen",
            5 : "Thu",
            6 : "Fri"
        }

        self.months = { # shifted +2
            1 : "13", #j
            2 : "14", #feb
            3 : "3", #mar
            4 : "4",
            5 : "5",
            6 : "6",
            7 : "7",
            8 : "8",
            9 : "9",
            10 : "10",
            11 : "11",
            12 : "12"
        }

        self.formula_inputs = {
            "w" : None, # output
            "dd" : None,
            "mm" : None,
            "y" : None,
            "c" : None
        }


        self.order_of_logic()

    def order_of_logic(self):
        self.get_inputs()
        self.get_year() # y, c 
        self.get_month() # mm
        self.get_dd() # d
        print(self.formula_inputs)

        self.formula()

    def get_inputs(self):
        self.date = str(input("Please enter a date (DD/MM/YYYY) : ")).split("/")
        return self.date
    
    def get_year(self):
        if (
            int(self.date[1]) == 1
            or int(self.date[1]) == 2
        ):
            self.to_strip = int(self.date[2]) - 1 
            self.to_strip = str(self.to_strip)
            self.formula_inputs["y"] = self.to_strip[-2:]
            self.formula_inputs["c"] = self.to_strip[:-2]
        else:
            self.to_strip = int(self.date[2])
            self.to_strip = str(self.to_strip)
            self.formula_inputs["y"] = self.to_strip[-2:]
            self.formula_inputs["c"] = self.to_strip[-2:]

    def get_month(self):
        self.month = int(self.date[1])
        self.formula_inputs["mm"] = self.months[self.month]

    def get_dd(self):
        self.formula_inputs["dd"] = self.date[0]

    def formula(self):

        self.dd = int(self.formula_inputs(["dd"])
        self.mm = int(self.formula_inputs(["mm"))
        self.y = int(self.formula_inputs(["y"]))
        self.c = int(self.formula_inputs(["c"]))
        

        self.formula_inputs["w"] = (self.dd + (13 * (self.mm + 1) / 5) + self.y + (self.y / 4) + (self.c / 4) - 2 * self.c) % 7

        print(self.formula_inputs["w"])

        


Solution()
