import pickle

# Separate class in case we want to handle serialization further
# Default file name: "gitdump.pickle"
class Picklizer:
    def __init__(self, data=None, file="gitdump.pickle"):
        if data != None:
            with open(file,"wb") as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            self.data = data

    def save(self, data, file="gitdump.pickle"):
        with open(file, "wb") as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def open(self, file="gitdump.pickle"):
        with open(file, "rb") as handle:
            self.data = pickle.load(handle)
        return self.data


def test_picklizer():
    pick = Picklizer()
    print(pick.open())