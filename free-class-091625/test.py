color = str(input("enter ur fav color : ")).lower()

match color:
    case "red":
        print("i like red too")
    case _:
        print(f"i dont like {color}, i prefer red")