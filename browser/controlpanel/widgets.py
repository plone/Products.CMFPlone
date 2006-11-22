from zope.app.form.browser import MultiCheckBoxWidget
from zope.app.form.browser import MultiSelectWidget
from zope.app.form.browser import RadioWidget
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFPlone import PloneMessageFactory as _


class MultiSelectTupleWidget(MultiSelectWidget):
    """Provide a selection list for the tuple to be selected."""

    def _toFieldValue(self, input):
        value = super(MultiSelectWidget, self)._toFieldValue(input)
        if isinstance(value, list):
            value = tuple(value)
        return value


def CalendarSessionWidget(field, request,
                          true=_("Use sessions to remember the calendars state"),
                          false=_("Don't use sessions to remember the calendars state")):
    """A widget for the selection of session usage for the CMFCalendar tool."""
    vocabulary = SimpleVocabulary.fromItems(((true, True), 
                                             (false, False)))
    return RadioWidget(field, vocabulary, request)


def WeekdayWidget(field, request):
    """A widget for the selection of weekdays."""
    vocabulary = SimpleVocabulary.fromItems((('Monday', 0), 
                                             ('Tuesday', 1),
                                             ('Wednesday', 2),
                                             ('Thursday', 3),
                                             ('Friday', 4),
                                             ('Saturday', 5),
                                             ('Sunday', 6)))
    return RadioWidget(field, vocabulary, request)

