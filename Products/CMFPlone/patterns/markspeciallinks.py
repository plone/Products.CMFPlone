from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPatternsSettings
from zope.interface import implements


class MarkSpecialLinksSettingsAdapter(object):
    implements(IPatternsSettings)

    def __init__(self, context, request, field):
        self.request = request
        self.context = context
        self.field = field
        self.properties = getToolByName(context, "portal_properties")

    def __call__(self):
        """Returns a settings dict if the markspeciallinks pattern is active
        """
        result = {}
        props = getattr(self.properties, 'site_properties')

        msl = props.getProperty('mark_special_links', 'false')
        elonw = props.getProperty('external_links_open_new_window', 'false')
        if msl == 'true' and elonw == 'true':
            result = {'data-pat-markspeciallinks':
                      '{"external_links_open_new_window": "true"}'}
        return result