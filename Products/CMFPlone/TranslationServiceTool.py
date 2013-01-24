"""
This tool requires a translation service which supports
the translate method and the default parameter.
"""
from zope.i18n import translate
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Acquisition import aq_get
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone import PloneLocalesMessageFactory as PLMF
from Products.CMFPlone.interfaces import ITranslationServiceTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

from i18nl10n import ulocalized_time, \
                     monthname_msgid, monthname_msgid_abbr, \
                     weekdayname_msgid, weekdayname_msgid_abbr, \
                     weekdayname_msgid_short, \
                     monthname_english, weekdayname_english


class TranslationServiceTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ Utility methods to access the translation machinery """

    id = 'translation_service'
    meta_type = 'Portal Translation Service Tool'
    toolicon = 'skins/plone_images/site_icon.png'
    security = ClassSecurityInfo()
    implements(ITranslationServiceTool)

    security.declarePublic('utranslate')
    def utranslate(self, *args, **kw):
        return self.translate(*args, **kw)

    security.declarePublic('translate')
    def translate(self, msgid, domain=None, mapping=None, context=None,
                  target_language=None, default=None):
        # Translate method for resticted code like skins.
        if context is not None:
            if not IBrowserRequest.providedBy(context):
                context = aq_get(context, 'REQUEST', None)

        return translate(msgid, domain=domain, mapping=mapping,
                         context=context, target_language=target_language,
                         default=default)

    security.declarePublic('encode')
    def encode(self, m, input_encoding=None, output_encoding=None,
               errors='strict'):
        # encode a give unicode type or string type to string type in encoding
        # output_encoding

        # check if input is not type unicode
        if not isinstance(m, unicode):
            if input_encoding is None:
                input_encoding = 'utf-8'
            m = unicode(str(m), input_encoding, errors)

        if output_encoding is None:
            output_encoding = 'utf-8'

        # return as type string
        return m.encode(output_encoding, errors)

    security.declarePublic('asunicodetype')
    def asunicodetype(self, m, input_encoding=None, errors='strict'):
        # create type unicode from type string

        if isinstance(m, unicode):
            return m

        if input_encoding is None:
            input_encoding = 'utf-8'

        # return as type unicode
        return unicode(str(m), input_encoding, errors)

    security.declarePublic('ulocalized_time')
    def ulocalized_time(self, time, long_format=None, time_only=None,
                        context=None, domain='plonelocales', request=None):
        # get some context if none is passed
        if context is None:
            context = self
        return ulocalized_time(time, long_format, time_only,
                               context, domain, request)

    security.declarePublic('day_msgid')
    def day_msgid(self, number, format=None):
        """ Returns the msgid which can be passed to the translation service
        for l10n of weekday names. Format is either None, 'a' or 's'.

        >>> ttool = TranslationServiceTool()

        >>> ttool.day_msgid(0)
        'weekday_sun'

        >>> ttool.day_msgid(6)
        'weekday_sat'

        >>> ttool.day_msgid(0, format='a')
        'weekday_sun_abbr'

        >>> ttool.day_msgid(3, format='s')
        'weekday_wed_short'
        """
        #
        if format == 's':
            # short format
            method = weekdayname_msgid_short
        elif format == 'a':
            # abbreviation
            method = weekdayname_msgid_abbr
        else:
            # long format
            method = weekdayname_msgid
        return method(number)

    security.declarePublic('month_msgid')
    def month_msgid(self, number, format=None):
        """ Returns the msgid which can be passed to the translation service
        for l10n of month names. Format is either '' or 'a' (long or
        abbreviation).

        >>> ttool = TranslationServiceTool()

        >>> ttool.month_msgid(1)
        'month_jan'

        >>> ttool.month_msgid(12)
        'month_dec'

        >>> ttool.month_msgid(6, format='a')
        'month_jun_abbr'
        """
        return 'a' == format \
               and monthname_msgid_abbr(number) \
               or monthname_msgid(number)

    security.declarePublic('month_english')
    def month_english(self, number, format=None):
        """ Returns the english name of month by number. Format is either '' or
        'a' (long or abbreviation).

        >>> ttool = TranslationServiceTool()

        >>> ttool.month_english(1)
        'January'

        >>> ttool.month_english(1, 'a')
        'Jan'
        """
        return monthname_english(number, format=format)

    security.declarePublic('month')
    def month(self, number, format=None, default=None):
        """ Returns a Message with the month name, that can be translated by
        the TAL engine. Format is either None or 'a' (long or abbreviation).
        """
        if default is None:
            default = monthname_english(number, format=format)
        value = 'a' == format \
                and monthname_msgid_abbr(number) \
                or monthname_msgid(number)
        return PLMF(value, default=default)

    security.declarePublic('weekday_english')
    def weekday_english(self, number, format=None):
        """ Returns the english name of a week by number. Format is
        either None, 'a' or 'p'.

        >>> ttool = TranslationServiceTool()

        >>> ttool.weekday_english(0)
        'Sunday'

        >>> ttool.weekday_english(6)
        'Saturday'

        >>> ttool.weekday_english(0, format='a')
        'Sun'

        >>> ttool.weekday_english(3, format='p')
        'Wed.'
        """
        return weekdayname_english(number, format=format)

InitializeClass(TranslationServiceTool)
