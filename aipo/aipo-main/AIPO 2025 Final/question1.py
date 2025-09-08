# inputs -> first line = single integar as n | n lines follow which contains string list

## the actual process :
## loop through each n_list word, and create a temporary list, reverse and compare
## then form an if statement whether to return NONE or the word

## process revised version 2 (improper reading of docs and therefor i had to ensure that i was doing what
## the problem was asking.. - inserting new letter to make possible)

# ! EDGE CASES TO REMEMBER ! 
# (if input is empty? if input only has 1 element? if input is very large? is input the wrong type?)

# outputs -> if the line is not a palindrome, return NONE otherwise if it is return the palindrome

def get_inputs():
    n = int(input())
    words = [input().strip() for x in range(n)]

    Solution(n = n, n_list = words)

def reverse_words(word):
    return word[::-1]

def check(word):
    return word == reverse_words(word)

def insertion(word):
    for pos in range(len(word) + 1):
        for x in "abcdefghijklmnopqrstuvwxyz":
            new_word = word[:pos] + x + word[pos:]
            if check(new_word):
                return new_word
            
    return "NONE"

def Solution(n, n_list):
    number = int(n)
    word_list = n_list

    for word in word_list:
        print(insertion(word))


get_inputs()