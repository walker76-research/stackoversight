import numpy as np
from datasketch import MinHash, MinHashLSHForest
from sanitizer import Sanitizer
from tokenizer import Tokenizer
from keyword_extractor import KeywordExtractor
from filter import Filter


class PipelineOutput(list):
    def __init__(self, items):
        super(PipelineOutput, self).__init__()
        self.items = items
        self.input = None
        self.forest = None

    def set_input(self, inp, processed=False):
        if processed:
            self.input = inp
        else:
            inp = Sanitizer.operation(inp)
            inp = Filter.operation(inp)
            inp = Tokenizer.operation(inp)
            inp = KeywordExtractor.operation(inp)
            self.input = inp

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)

    def get_length(self, index=None):
        if index is None:
            return len(self.items)
        else:
            try:
                return len(self.items[index])
            except IndexError as e:
                return e

    def print(self, index=None):
        if index is None:
            for ind, it in enumerate(self.items):
                print("=INDEX: " + str(ind) + "=")
                print(it)
        else:
            try:
                print("=INDEX: " + str(index) + "=")
                print(self.items[index])
            except IndexError:
                print("Index out of bounds on pipeline print!")

    # Forms the forest for LSH
    def get_lsh(self):
        if self.input is None:
            return None

        minhash = []

        for s in self.items:
            m = MinHash(num_perm=128)
            for q in s:
                m.update(q.encode('utf8'))
            minhash.append(m)

        forest = MinHashLSHForest(num_perm=128)

        for i, m in enumerate(minhash):
            forest.add(i, m)

        forest.index()
        self.forest = forest

        return forest

    # Default item to query by should be the input of the pipeline obj
    # Otherwise you can specify
    # Outputs top 5 most similar results
    def query(self, item=None):
        if item is None:
            if self.input is not None:
                item = self.input
            else:
                return None

        m = MinHash(num_perm=128)
        for s in item:
            m.update(s.encode('utf8'))
        out = np.array(self.forest.query(m, 5))
        if len(out) == 0:
            return None
        else:
            return out
