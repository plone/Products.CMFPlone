from ZTUtils.Batch import Batch as ZTUBatch
from ZTUtils import make_query
from ExtensionClass import Base

# These have to be duplicated from ZTUtils.Batch to use the correct Batch
# class, otherwise orphans will come out wrong in the 'show x next messages'.


class LazyPrevBatch(Base):

    def __of__(self, parent):
        return Batch(parent._sequence, parent._size,
                     parent.first - parent._size + parent.overlap, 0,
                     parent.orphan, parent.overlap)


class LazyNextBatch(Base):

    def __of__(self, parent):
        if parent.end >= (parent.last + parent.size):
            return None
        return Batch(parent._sequence, parent._size,
                     parent.end - parent.overlap, 0,
                     parent.orphan, parent.overlap)


class LazySequenceLength(Base):

    def __of__(self, parent):
        _sequence = parent._sequence
        l = getattr(_sequence, 'actual_result_count', len(_sequence))
        parent.sequence_length = l
        return l


class Batch(ZTUBatch):
    """Create a sequence batch"""
    __allow_access_to_unprotected_subobjects__ = 1

    previous = LazyPrevBatch()
    next = LazyNextBatch()
    sequence_length = LazySequenceLength()

    size = first= start = end = orphan = overlap = navlist = None
    numpages = pagenumber = pagerange = pagerangeend = pagerangestart = pagenumber = quantumleap = None

    def __init__(self, sequence, size, start=0, end=0, orphan=0, overlap=0, pagerange=7, quantumleap=0, b_start_str='b_start'):
        """ Encapsulate sequence in batches of size
        sequence    - the data to batch.
        size        - the number of items in each batch. This will be computed if left out.
        start       - the first element of sequence to include in batch (0-index)
        end         - the last element of sequence to include in batch (0-index, optional)
        orphan      - the next page will be combined with the current page if it does not contain more than orphan elements
        overlap     - the number of overlapping elements in each batch
        pagerange   - the number of pages to display in the navigation
        quantumleap - 0 or 1 to indicate if bigger increments should be used in the navigation list for big results.
        b_start_str - the request variable used for start, default 'b_start'
        """
        start = start + 1
        self._sequence = sequence
        self._size = size
        sequence_length = self.sequence_length

        start, end, sz = opt(start, end, size, orphan, sequence_length)

        self.size = sz
        self.start = start
        self.end = end
        self.orphan = orphan
        self.overlap = overlap
        self.first = max(start - 1, 0)
        self.length = self.end - self.first

        self.b_start_str = b_start_str

        self.last = sequence_length - size

        # Set up next and previous
        if self.first == 0:
            self.previous = None

        # Set up the total number of pages
        self.numpages = calculate_pagenumber(self.sequence_length - self.orphan, self.size, self.overlap)

        # Set up the current page number
        self.pagenumber = calculate_pagenumber(self.start, self.size, self.overlap)

        # Set up pagerange for the navigation quick links
        self.pagerange, self.pagerangestart, self.pagerangeend = calculate_pagerange(self.pagenumber, self.numpages, pagerange)

        # Set up the lists for the navigation: 4 5 [6] 7 8
        #  navlist is the complete list, including pagenumber
        #  prevlist is the 4 5 in the example above
        #  nextlist is 7 8 in the example above
        self.navlist = self.prevlist = self.nextlist = []
        if self.pagerange and self.numpages >= 1:
            self.navlist = range(self.pagerangestart, self.pagerangeend)
            self.prevlist = range(self.pagerangestart, self.pagenumber)
            self.nextlist = range(self.pagenumber + 1, self.pagerangeend)

        # QuantumLeap - faster navigation for big result sets
        self.quantumleap = quantumleap
        self.leapback = self.leapforward = []
        if self.quantumleap:
            self.leapback = calculate_leapback(self.pagenumber, self.numpages, self.pagerange)
            self.leapforward = calculate_leapforward(self.pagenumber, self.numpages, self.pagerange)

    def pageurl(self, formvariables, pagenumber=-1):
        """ Makes the url for a given page """
        if pagenumber == -1:
            pagenumber = self.pagenumber
        b_start = pagenumber * (self.size - self.overlap) - self.size
        return make_query(formvariables, {self.b_start_str: b_start})

    def navurls(self, formvariables, navlist=[]):
        """ Returns the page number and url for the navigation quick links """
        if not navlist:
            navlist = self.navlist
        return map(lambda x, formvariables = formvariables: (x, self.pageurl(formvariables, x)), navlist)

    def prevurls(self, formvariables):
        """ Helper method to get prev navigation list from templates """
        return self.navurls(formvariables, self.prevlist)

    def nexturls(self, formvariables):
        """ Helper method to get next navigation list from templates """
        return self.navurls(formvariables, self.nextlist)

    def __getitem__(self, index):
        actual = getattr(self._sequence, 'actual_result_count', None)
        if actual is not None and actual != len(self._sequence):
            # optmized batch that contains only the wanted items in the sequence
            return self._sequence[index]
        if index < 0:
            if index + self.end < self.first:
                raise IndexError(index)
            return self._sequence[index + self.end]
        if index >= self.length:
            raise IndexError(index)
        return self._sequence[index + self.first]


# Calculate start, end, batchsize
# This is copied from ZTUtils.Batch.py because orphans were not correct there.
# 04/16/04 modified by Danny Bloemendaal (_ender_). Removed try/except structs because
# in some situations they cause some unexpected problems.
# Also fixed some problems with the orphan stuff. Seems to work now.
def opt(start, end, size, orphan, sequence_length):
    length = sequence_length
    if size < 1:
        if start > 0 and end > 0 and end >= start:
            size = end + 1 - start
        else:
            size = 25
    if start > 0:
        if start>length:
            start = length
        if end > 0:
            if end < start:
                end = start
        else:
            end = start + size - 1
            if (end+orphan)>=length:
                end = length
    elif end > 0:
        if (end)>length:
            end = length
        start = end + 1 - size
        if start - 1 < orphan:
            start = 1
    else:
        start = 1
        end = start + size - 1
        if (end+orphan)>=length:
            end = length
    return start, end, size


def calculate_pagenumber(elementnumber, batchsize, overlap=0):
    """ Calculate the pagenumber for the navigation """
    # To find first element in a page,
    # elementnumber = pagenumber * (size - overlap) - size (- orphan?)
    try:
        pagenumber, remainder = divmod(elementnumber, batchsize - overlap)
    except ZeroDivisionError:
        pagenumber, remainder = divmod(elementnumber, 1)
    if remainder > overlap:
        pagenumber = pagenumber + 1
    pagenumber = max(pagenumber, 1)
    return pagenumber


def calculate_pagerange(pagenumber, numpages, pagerange):
    """ Calculate the pagerange for the navigation quicklinks """
    # Pagerange is the number of pages linked to in the navigation, odd number
    pagerange = max(0, pagerange + pagerange % 2 - 1)
    # Making sure the list will not start with negative values
    pagerangestart = max(1, pagenumber - (pagerange - 1) / 2)
    # Making sure the list does not expand beyond the last page
    pagerangeend = min(pagenumber + (pagerange - 1) / 2, numpages) + 1
    return pagerange, pagerangestart, pagerangeend


def calculate_quantum_leap_gap(numpages, pagerange):
    """ Find the QuantumLeap gap. Current width of list is 6 clicks (30/5) """
    return int(max(1, round(float(numpages - pagerange)/30))*5)


def calculate_leapback(pagenumber, numpages, pagerange):
    """ Check the distance between start and 0 and add links as necessary """
    leapback = []
    quantum_leap_gap = calculate_quantum_leap_gap(numpages, pagerange)
    num_back_leaps = max(0, min(3, int(round(float(pagenumber - pagerange)/quantum_leap_gap) - 0.3)))
    if num_back_leaps:
        pagerange, pagerangestart, pagerangeend = calculate_pagerange(pagenumber, numpages, pagerange)
        leapback = range(pagerangestart - num_back_leaps * quantum_leap_gap, pagerangestart, quantum_leap_gap)
    return leapback


def calculate_leapforward(pagenumber, numpages, pagerange):
    """ Check the distance between end and length and add links as necessary """
    leapforward = []
    quantum_leap_gap = calculate_quantum_leap_gap(numpages, pagerange)
    num_forward_leaps = max(0, min(3, int(round(float(numpages - pagenumber - pagerange)/quantum_leap_gap) - 0.3)))
    if num_forward_leaps:
        pagerange, pagerangestart, pagerangeend = calculate_pagerange(pagenumber, numpages, pagerange)
        leapforward = range(pagerangeend-1 + quantum_leap_gap, pagerangeend-1 + (num_forward_leaps+1) * quantum_leap_gap, quantum_leap_gap)
    return leapforward
