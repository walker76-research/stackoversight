import numpy as np
from datasketch import MinHash, MinHashLSHForest


class PipelineOutput(list):
    def __init__(self, items, raw):
        super(PipelineOutput, self).__init__()
        self.__items = items
        self.__input = None
        self.__forest = None
        self.__results = []
        self.__hashlist = []
        self.__hash_results = []
        self.__raw = raw

    def set_input(self, inp):
        self.__input = inp

    def __str__(self):
        return str(self.__items)

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
    def form_lsh(self, input=None):
        if self.__input is None and input is not None:
            self.__input = input
        elif input is None:
            return None

        minhash = []

        for s in self.__items:
            m = MinHash(num_perm=256)
            for q in s:
                m.update(q.encode('utf8'))
            minhash.append(m)

        forest = MinHashLSHForest(num_perm=256)

        for i, m in enumerate(minhash):
            forest.add(i, m)

        forest.index()
        self.__forest = forest
        self.__hashlist = minhash

        return forest

    def __get_jaccard(self, item):
        results = []
        if self.__hash_results is not None:
            for i, x in enumerate(self.__hash_results):
                results.append((x, self.__hashlist[x].jaccard(item)))
        return results

    def __get_snippets(self):
        result = []
        for x in self.__hash_results:
            result.append(self.__raw[x])
        return result

    # Default item to query by should be the input of the pipeline obj
    # Otherwise you can specify
    # Outputs top 5 most similar results
    def query(self, item=None):
        query_output = QueryOutput()
        if item is None:
            if self.__input is not None:
                item = self.__input
            else:
                return query_output

        m = MinHash(num_perm=256)
        for s in item:
            m.update(s.encode('utf8'))
        query = self.__forest.query(m, 5)
        out = np.array(query)
        self.__hash_results = query
        if len(out) == 0:
            return query_output
        else:
            self.__results = QueryOutput(out, self.__get_jaccard(m), self.__get_snippets())
            return self.__results

    def __get_results(self):
        return self.__results

    results = property(__get_results)


class QueryOutput:

    def __init__(self, results=None, similarity=None, snippets=None):
        self.__results = results if results is not None else []
        self.__similarity = similarity if similarity is not None else []
        self.__snippets = snippets if snippets is not None else []
        self.num_results = len(results) if results is not None else 0
        self.message = f"There are {self.num_results} matches found" if self.num_results > 0 else "No matches found"

    def get_results(self):
        return self.__results

    def get_snippets(self):
        return self.__snippets

    def get_snippet(self, index):
        if len(self.__snippets) > 0:
            return self.__snippets[index]
        else:
            return None

    def get(self):
        return self.__similarity

    def get_jaccard(self, index):
        if len(self.__similarity) > 0:
            return self.__similarity[index]
        else:
            return None