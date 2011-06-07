from zope.interface import Interface


class ITranslationServiceTool(Interface):
    """ Utility methods to access the translation machinery
    """

    def translate(*args, **kw):
        """Translate method to access the translation service
           from resticted code like skins.
        """

    def encode(m, input_encoding=None, output_encoding=None, errors='strict'):
        """Encode a give unicode type or string type to string type in encoding
           output_encoding
        """

    def asunicodetype(m, input_encoding=None, errors='strict'):
        """Create type unicode from type string"""

    def ulocalized_time(time, long_format = None, time_only = None, context = None, domain='plonelocales'):
        """Returns localized time."""

    def day_msgid(number, format=''):
        """Returns the msgid which can be passed to the translation service for
           l10n of weekday names. Format is either '', 'a' or 's'.
        """

    def month_msgid(number, format=''):
        """Returns the msgid which can be passed to the translation service for
           l10n of month names. Format is either '' or 'a' (long or abbreviation).
        """

    def month_english(number, format=''):
        """Returns the english name of month by number. Format is either '' or
           'a' (long or abbreviation).
        """

    def weekday_english(number, format=''):
        """Returns the english name of a week by number. Format is either '',
           'a' or 'p'.
        """
