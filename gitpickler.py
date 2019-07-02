import pickle

# Separate class in case we want to handle serialization further
class Picklizer:
    def __init__(self, data):
        with open("gitdump.pickle","wb") as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def open(self):
        with open("gitdump.pickle", "rb") as handle:
            return pickle.load(handle)
