class IndexIterator:
    __allow_access_to_unprotected_subobjects__ = 1 

    def __init__(self, upper=100):
        self.upper=upper
        self.pos=0

    def next(self):
        if self.pos <= self.upper:
            self.pos += 1
            return self.pos
        raise KeyError, 'Reached upper bounds'


