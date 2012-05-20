from ZTUtils import make_query

from plone.batching.batch import QuantumBatch
from plone.batching.utils import calculate_pagerange

from zope.deprecation import deprecated


class Batch(QuantumBatch):

    b_start_str = 'b_start'

    def __init__(self, sequence, size, start=0, end=0, orphan=0,
                 overlap=0, pagerange=7, quantumleap=0,
                 b_start_str='b_start'):
        super(Batch, self).__init__(sequence, size, start,
                                    end, orphan, overlap,
              pagerange, quantumleap)
        self.b_start_str = b_start_str

    def __len__(self):
        return self.length
    __len__ = deprecated(__len__,
        ('Using len() for getting the actual pagesize is deprecated. Use the '
         '`pagesize` attribute instead.'))

    def initialize(self, start, end, size):
        super(Batch, self).initialize(start, end, size)
        self.pagerange, self.pagerangestart, self.pagerangeend = \
            calculate_pagerange(self.pagenumber, self.numpages, self.pagerange)

    def pageurl(self, formvariables, pagenumber=-1):
        """ Makes the url for a given page """
        if pagenumber == -1:
            pagenumber = self.pagenumber
        b_start = pagenumber * (self.pagesize - self.overlap) - self.pagesize
        return make_query(formvariables, {self.b_start_str: b_start})

    def navurls(self, formvariables, navlist=[]):
        """ Returns the page number and url for the navigation quick links """
        if not navlist:
            navlist = self.navlist
        return map(lambda x, formvariables=formvariables:
                (x, self.pageurl(formvariables, x)), navlist)

    def prevurls(self, formvariables):
        """ Helper method to get prev navigation list from templates """
        return self.navurls(formvariables, self.previous_pages)

    def nexturls(self, formvariables):
        """ Helper method to get next navigation list from templates """
        return self.navurls(formvariables, self.next_pages)

    prevlist = QuantumBatch.previous_pages
    nextlist = QuantumBatch.next_pages
