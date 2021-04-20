# This module delivers the global patterns settings
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IPatternsSettings
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView


class PatternsSettingsView(BrowserView):
    """
    Default patterns settings
    """

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )
        # do not use getSite because it's possible it could be different
        # than the actual portal url
        portal_url = portal_state.portal_url()
        result = {
            "data-base-url": self.context.absolute_url(),
            "data-view-url": context_state.view_url(),
            "data-portal-url": portal_url,
            "data-i18ncatalogurl": portal_url + "/plonejsi18n",
        }

        # first, check for any adapters that need pattern data defined
        adapters = getAdapters((self.context, self.request, None), IPatternsSettings)
        [result.update(x[1]()) for x in adapters]

        # Resources Registered UI patterns can override adapters
        registry = getUtility(IRegistry)
        pattern_options = registry.get("plone.patternoptions", {})
        for key, value in pattern_options.items():
            result["data-pat-" + key] = value

        return result
