import numpy as np
from datasketch import MinHash, MinHashLSHForest


class PipelineOutput(list):
    def __init__(self, items):
        super(PipelineOutput, self).__init__()
        self.__items = items
        self.__input = None
        self.__forest = None
        self.__results = []

    def set_input(self, inp):
        self.__input = inp

    def __getitem__(self, item):
        return self.__items[item]

    def __len__(self):
        return len(self.__items)

    def get_length(self, index=None):
        if index is None:
            return len(self.__items)
        else:
            try:
                return len(self.__items[index])
            except IndexError as e:
                return e

    def print(self, index=None):
        if index is None:
            for ind, it in enumerate(self.__items):
                print("=INDEX: " + str(ind) + "=")
                print(it)
        else:
            try:
                print("=INDEX: " + str(index) + "=")
                print(self.__items[index])
            except IndexError:
                print("Index out of bounds on pipeline print!")

    # Forms the forest for LSH
    def form_lsh(self):
        if self.__input is None:
            return None

        minhash = []

        for s in self.__items:
            m = MinHash(num_perm=128)
            for q in s:
                m.update(q.encode('utf8'))
            minhash.append(m)

        forest = MinHashLSHForest(num_perm=128)

        for i, m in enumerate(minhash):
            forest.add(i, m)

        forest.index()
        self.__forest = forest

        return forest

    # Default item to query by should be the input of the pipeline obj
    # Otherwise you can specify
    # Outputs top 5 most similar results
    def query(self, item=None):
        if item is None:
            if self.__input is not None:
                item = self.__input
            else:
                return None

        m = MinHash(num_perm=128)
        for s in item:
            m.update(s.encode('utf8'))
        out = np.array(self.__forest.query(m, 5))
        if len(out) == 0:
            return None
        else:
            self.__results = out
            return out

    def __get_results(self):
        return self.__results

    results = property(__get_results)
