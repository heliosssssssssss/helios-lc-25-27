import math 
import time 

class solution():
    def get_inputs():
        test_cases = int(input())
        test_case_map = []

        for test_case in range(test_cases):
            loa = int(input()) # length of a
            a = str(input()) # string a 
            m = int(input()) # lengths of b, c 
            b = str(input()) # string b
            c = str(input()) # string c, consisting of V, D which is the distrubtion of characters
                             # of string b between Dima & Vlad (hence, D,V) if c

            ew_tc = test_case_map.append([loa, a, m, b, c])
            print(ew_tc)


solution.get_inputs()   


