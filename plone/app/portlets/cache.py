from StringIO import StringIO

from zope import component
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.memoize import ram

def get_language(context, request):
    portal_state = component.getMultiAdapter(
        (context, request), name=u'plone_portal_state')
    return portal_state.locale().getLocaleID()

def render_cachekey(fun, self):
    key = StringIO()
    print >> key, getToolByName(aq_inner(self.context), 'portal_url')()
    print >> key, get_language(aq_inner(self.context), self.request)

    def add(brain):
        key.write(brain.getPath())
        key.write('\n')
        key.write(brain.modified)
        key.write('\n\n')

    catalog = getToolByName(self.context, 'portal_catalog')
    for brain in self._data():
        add(brain)

    return key.getvalue()
