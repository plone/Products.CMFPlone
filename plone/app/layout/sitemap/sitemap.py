from Products.Five import BrowserView
from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from gzip import GzipFile
from cStringIO import StringIO

from plone.memoize import ram

def _render_cachekey(fun, self):
    # Cache by filename
    mtool = getToolByName(self.context, 'portal_membership')
    if not mtool.isAnonymousUser():
        raise ram.DontCache

    url_tool = getToolByName(self.context, 'portal_url')
    catalog = getToolByName(self.context, 'portal_catalog')
    counter = catalog.getCounter()
    return '%s/%s/%s' % (url_tool(), self.filename, counter)


class SiteMapView(BrowserView):
    """Creates the sitemap as explained in the specifications.

    http://www.sitemaps.org/protocol.php
    """

    template = ViewPageTemplateFile('sitemap.xml')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filename = 'sitemap.xml.gz'

    def objects(self):
        """Returns the data to create the sitemap."""
        catalog = getToolByName(self.context, 'portal_catalog')
        for item in catalog.searchResults({'Language': 'all'}):
            yield {
                'loc': item.getURL(),
                'lastmod': item.modified.ISO8601(),
                #'changefreq': 'always', # hourly/daily/weekly/monthly/yearly/never
                #'prioriy': 0.5, # 0.0 to 1.0
            }

    @ram.cache(_render_cachekey)
    def generate(self):
        """Generates the Gzipped sitemap."""
        xml = self.template()
        fp = StringIO()
        gzip = GzipFile(self.filename, 'w', 9, fp)
        gzip.write(xml)
        gzip.close()
        data = fp.getvalue()
        fp.close()
        return data

    def __call__(self):
        """Checks if the sitemap feature is enable and returns it."""
        sp = getToolByName(self.context, 'portal_properties').site_properties
        if not sp.enable_sitemap:
            raise NotFound(self.context, self.filename, self.request)

        self.request.response.setHeader('Content-Type',
                                        'application/octet-stream')
        return self.generate()
