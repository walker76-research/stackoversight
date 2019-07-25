class ProcessingStep(object):
    def __init__(self):
        self.results = []
        self._name = None

    def process(self, items):
        for item in items:
            result = self.operation(item)
            self.results.append(result)
        return self.results

    def get(self):
        return self.results

    def operation(self, item):
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError
