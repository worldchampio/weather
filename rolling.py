"""
FIFO queue maintaining length n
"""
class Queue:
    def __init__(self, n):
        self.n = n
        self.queue = []
    def insert(self, element):
        self.queue.append(element)
        if len(self.queue) > self.n:
            self.queue.pop(0)
    def average(self):
        sum = 0.0
        for element in self.queue: sum+=element
        return sum/len(self.queue)
"""
Calculate the rolling average for every
element in a dataset with a windowsize
"""
class RollingAverage:
    def __init__(self, dataset, windowSize):
        if windowSize > len(dataset):
            print("windowsize should be smaller than dataset length.")
            return []
        self.rollingAverage = []
        queue = Queue(windowSize)
        for element in dataset:
            queue.insert(element)
            self.rollingAverage.append(queue.average())
    def getData(self): 
        return self.rollingAverage