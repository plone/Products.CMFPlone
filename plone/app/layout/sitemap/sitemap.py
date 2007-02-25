from Products.Five import BrowserView
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cStringIO import StringIO
from gzip import GzipFile


class SiteMapView(BrowserView):
    
    template = ViewPageTemplateFile('sitemap.xml')
    
    def objects(self):
        """create the google sitemap as explained in 
        
        https://www.google.com/webmasters/tools/docs/en/protocol.html
        
        """
        # create the sitemap
        catalog = getToolByName(self.context,"portal_catalog")
        all = catalog.searchResults()
        
        return all
        
    def __call__(self):
        """render the template and compress it"""
        # check if we are allowed to be shown
        sp = getToolByName(self.context,'portal_properties').site_properties
        if not sp.enable_sitemap:
            raise NotFound(self.context, "sitemap.xml.gz", self.request)

        # set the headers
        self.request.RESPONSE.setHeader("Content-Type",
                "application/octet-stream")
        xml = self.template()
        fp = StringIO()
        gzip = GzipFile("sitemap.xml.gz","w",9,fp)
        gzip.write(xml)
        gzip.close()
        data = fp.getvalue()
        fp.close()
        return data

        
