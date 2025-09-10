class RFCipher:

    def __init__(self, text_to_encode : str, key : int):
        self.text_to_encode = text_to_encode
        self.key = key
        self.matrix2d = []
        self.blank = "*"

        print(self.text_to_encode, self.key)
        self.order_of_logic()
    
    def order_of_logic(self):
        self.generate_matrix()
        self.insert_matrix()

        print(self.matrix2d)

    def generate_matrix(self):

        for row in range(self.key): # GENERATE ROW
            self.matrix2d.append([])
            for _c in range(len(self.text_to_encode) - 1): # GENERATE COL
                self.matrix2d[row].append(self.blank)

    def insert_matrix(self):
        matrix = self.matrix2d

        designated_row = 0 
        designated_col = 0
        row_reset = self.key
        
        for letter in range(0, len(self.text_to_encode) - 1):

            if designated_row == row_reset: # RESET ROW 
                designated_row = 0 
                

            print(letter, designated_row)
            self.matrix2d[designated_row][designated_col] = self.text_to_encode

            if designated_row != row_reset:
                designated_row += 1





    def encrypt():
        pass

    def decrypt():
        pass
                
            


    

RFCipher("hello", 3)