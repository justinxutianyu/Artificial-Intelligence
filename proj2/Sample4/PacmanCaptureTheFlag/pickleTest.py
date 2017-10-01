import pickle

favorite_color = {"lion": "yellow", "kitty": "red"}

pickle.dump(favorite_color, open("save.p", "wb"))

readfavorite_color = pickle.load(open("save.p","rb"))

print readfavorite_color
            
