from Acquisition import aq_inner
from Products.Five import BrowserView
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cStringIO import StringIO
from gzip import GzipFile

from plone.memoize import ram

def _render_cachekey(fun, self):
    return "sitemap" # fixed cache key only for that one as the sitemap is global

class SiteMapView(BrowserView):

    template = ViewPageTemplateFile('sitemap.xml')

    def objects(self):
        """create the google sitemap as explained in 
        
        https://www.google.com/webmasters/tools/docs/en/protocol.html
        
        """
        # create the sitemap
        catalog = getToolByName(aq_inner(self.context), "portal_catalog")
        for item in catalog.searchResults({'Language':'all'}):
            yield {
                'url': item.getURL(),
                'modificationdate': item.modified.toZone("GMT+0").strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            }

    @ram.cache(_render_cachekey)
    def generate(self):
        """generate the gzipped sitemap"""
        xml = self.template()
        fp = StringIO()
        gzip = GzipFile("sitemap.xml.gz","w",9,fp)
        gzip.write(xml)
        gzip.close()
        data = fp.getvalue()
        fp.close()
        return data
        
    def __call__(self):
        """render the template and compress it"""
        # check if we are allowed to be shown"
        sp = getToolByName(aq_inner(self.context), 'portal_properties').site_properties
        if not sp.enable_sitemap:
            raise NotFound(self.context, "sitemap.xml.gz", self.request)

        # set the headers
        self.request.RESPONSE.setHeader("Content-Type",
                "application/octet-stream")

        return self.generate()