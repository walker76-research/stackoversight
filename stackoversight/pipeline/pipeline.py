class Pipeline(object):
    def __init__(self, steps=None):
        if steps is None:
            steps = []
        self.steps = steps

    def set_steps(self, steps):
        self.steps = steps
    
    def feed(self, items):
        # Feed the item into one step, get the result, feed the
        # result to the next step and so on.
        for step in self.steps:
            step.process(items)
            items = step.get()

        return PipelineOutput(items)


class PipelineOutput(list):
    def __init__(self, items):
        super(PipelineOutput, self).__init__()
        self.items = items

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

    def get_unique_id(self, index):
        return 10
