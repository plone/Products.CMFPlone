from ZTUtils import Iterator

class IndexIterator(Iterator):
    __allow_access_to_unprotected_subobjects__ = 1 

    def __init__(self, upper=100):
        self.seq=[x for x in xrange(0,upper)]
        self.pos=0

    def next(self):
        if self.pos<len(self.seq):
            self.pos+=1
            return self.seq[self.pos]


