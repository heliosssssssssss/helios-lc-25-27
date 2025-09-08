def capital_indexes(i):
    word = i
    pos_table = []

    for position, letter in enumerate(word): 
        if str(letter).isupper() == True: 
            pos_table.append(position)

    return pos_table

print(capital_indexes("HI"))