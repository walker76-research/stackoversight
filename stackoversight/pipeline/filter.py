class Filter(object):
    def __init__(self):
        self.results = []

    def process(self, items):
        for item in items:
            for result in self.operation(item):
                self.results.append(result)

    def get(self):
        return self.results

    def operation(self, item):
        raise NotImplementedError
