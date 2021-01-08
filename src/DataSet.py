

class DataSet:
    def __init__(self):
        self.data = set()
        self.data.clear()
        return

    def add(self, element):
        self.data.add(element)

    def test(self, element):
        res = (element in self.data)
        return res

    def length(self):
        return len(self.data)

    def isdisjoint(self, ds2):
        return self.data.isdisjoint(ds2.data)
