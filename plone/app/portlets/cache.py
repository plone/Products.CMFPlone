from zope import component
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName


def get_language(context, request):
    portal_state = component.getMultiAdapter(
        (context, request), name=u'plone_portal_state')
    return portal_state.locale().getLocaleID()


def render_cachekey(fun, self):
    """
    Generates a key based on:

    * Portal URL
    * Negotiated language
    * Anonymous user flag
    * Portlet manager
    * Assignment
    * Fingerprint of the data used by the portlet

    """
    context = aq_inner(self.context)

    def add(brain):
        path = brain.getPath().decode('ascii', 'replace')
        return "%s\n%s\n\n" % (path, brain.modified)
    fingerprint = "".join(map(add, self._data()))

    anonymous = getToolByName(context, 'portal_membership').isAnonymousUser()

    return "".join((
        getToolByName(aq_inner(self.context), 'portal_url')(),
        get_language(aq_inner(self.context), self.request),
        str(anonymous),
        self.manager.__name__,
        self.data.__name__,
        fingerprint))
