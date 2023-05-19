"""
Calculate the rolling average for every
element in a dataset with a windowsize
"""
class RollingAverage:
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
        
    def __init__(self, dataset, windowSize):
        if windowSize > len(dataset):
            print("windowsize should be smaller than dataset length.")
            return []
        self.rollingAverage = []
        window = self.Queue(windowSize)
        for element in dataset:
            window.insert(element)
            self.rollingAverage.append(window.average())
    def get_data(self): 
        return self.rollingAverage