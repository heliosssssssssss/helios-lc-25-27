metatable = {
    "H1" : [90, 100],
    "H2" : [80, 89],
    "H3" : [70, 79],
    "H4" : [60, 69],
    "H5" : [50, 59],
    "H6" : [40, 49],
    "H7" : [30, 39],
    "H8" : [0, 29]
}

unique_texts = {
    "H1" : "well done",
    "H2" : "you nearly got a h1, better luck next time",
    "H3" : "i kind of expected better, you got this tho",
    "H4" : "just keep studying and you will be getting H2s+",
    "H5" : "barely tipping the pass point man",
    "H6" : "you failed",
    "H7" : "are u even studying",
    "H8" : "cooked icl",
}

grade = int(input("Please tell me your grade : "))

def solution(grade : int):

    ## VALIDATION

    for rank in metatable:
        score_def = rank
        limit_left = metatable[rank][0]
        limit_right = metatable[rank][1]

        #print(score_def, limit_left, limit_right)

        if (
            grade >= limit_left
            and grade <= limit_right
        ):
            
            print(f"""
[===================================================================================================================]

            
 /$$       /$$$$$$$$  /$$$$$$  /$$    /$$ /$$$$$$ /$$   /$$  /$$$$$$         /$$$$$$  /$$$$$$$$ /$$$$$$$  /$$$$$$$$
| $$      | $$_____/ /$$__  $$| $$   | $$|_  $$_/| $$$ | $$ /$$__  $$       /$$__  $$| $$_____/| $$__  $$|__  $$__/
| $$      | $$      | $$  \ $$| $$   | $$  | $$  | $$$$| $$| $$  \__/      | $$  \__/| $$      | $$  \ $$   | $$   
| $$      | $$$$$   | $$$$$$$$|  $$ / $$/  | $$  | $$ $$ $$| $$ /$$$$      | $$      | $$$$$   | $$$$$$$/   | $$   
| $$      | $$__/   | $$__  $$ \  $$ $$/   | $$  | $$  $$$$| $$|_  $$      | $$      | $$__/   | $$__  $$   | $$   
| $$      | $$      | $$  | $$  \  $$$/    | $$  | $$\  $$$| $$  \ $$      | $$    $$| $$      | $$  \ $$   | $$   
| $$$$$$$$| $$$$$$$$| $$  | $$   \  $/    /$$$$$$| $$ \  $$|  $$$$$$/      |  $$$$$$/| $$$$$$$$| $$  | $$   | $$   
|________/|________/|__/  |__/    \_/    |______/|__/  \__/ \______/        \______/ |________/|__/  |__/   |__/   
                                                                                                                   
                                                                                                                   
[===================================================================================================================]                                                                                                                 

            You have received a {score_def} in your exam. | Actual Precentage: {grade}%
            Examiner Note : {unique_texts[score_def]} 
                  

""")

solution(grade = grade)
input()