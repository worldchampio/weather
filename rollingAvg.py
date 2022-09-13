"""
Calculate the rolling average for every
element in a dataset with a windowsize
"""
class RollingWindow:
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

class RollingAverage:
    def __init__(self, dataset, windowSize):
        if windowSize > len(dataset):
            print("windowsize should be smaller than dataset length.")
            return []
        self.rollingAverage = []
        window = RollingWindow(windowSize)
        for element in dataset:
            window.insert(element)
            self.rollingAverage.append(window.average())
    def getData(self): 
        return self.rollingAverage