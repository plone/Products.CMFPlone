# Avoid OverflowErrors in Date*Indexes

from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
from DateTime import DateTime

maxDate = DateTime(4008, 0)


def _convert(self, value, default=None):
    try:
        return self.__old_convert(value, default)
    except OverflowError:
        return self.__old_convert(maxDate, default)

DateIndex.__old_convert = DateIndex._convert
DateIndex._convert = _convert


def _convertDateTime(self, value):
    try:
        return self.__old_convertDateTime(value)
    except OverflowError:
        return self.__old_convertDateTime(maxDate)

DateRangeIndex.__old_convertDateTime = DateRangeIndex._convertDateTime
DateRangeIndex._convertDateTime = _convertDateTime
