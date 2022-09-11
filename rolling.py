class Queue:
    def __init__(self,limit):
        self.limit = limit
        self.data = []
    def insert(self, entry):
        self.data.append(entry)
        if len(self.data) > self.limit:
            self.data.pop(0)
    def average(self):
        sum = 0.0
        for element in self.data:
            sum+=element
        return sum/len(self.data)

class RollingAverage:
    def __init__(self, data, limit):
        self.rollingAverage = []
        queue = Queue(limit)
        for element in data:
            queue.insert(element)
            self.rollingAverage.append(queue.average())
    def getData(self):
        return self.rollingAverage