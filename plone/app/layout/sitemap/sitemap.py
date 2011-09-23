from BTrees.OOBTree import OOBTree
from Products.Five import BrowserView
from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
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
        query = {'Language': 'all'}
        utils = getToolByName(self.context, 'plone_utils')
        query['portal_type'] = utils.getUserFriendlyTypes()
        ptool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(ptool, 'site_properties')
        typesUseViewActionInListings = frozenset(
            siteProperties.getProperty('typesUseViewActionInListings', [])
            )

        is_plone_site_root = IPloneSiteRoot.providedBy(self.context)
        if not is_plone_site_root:
            query['path'] = '/'.join(self.context.getPhysicalPath())

        query['is_default_page'] = True
        default_page_modified = OOBTree()
        for item in catalog.searchResults(query):
            key = item.getURL().rsplit('/', 1)[0]
            value = (item.modified.micros(), item.modified.ISO8601())
            default_page_modified[key] = value

        # The plone site root is not catalogued.
        if is_plone_site_root:
            loc = self.context.absolute_url()
            date = self.context.modified()
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            yield {
                'loc': loc,
                'lastmod': lastmod,
                #'changefreq': 'always', # hourly/daily/weekly/monthly/yearly/never
                #'prioriy': 0.5, # 0.0 to 1.0
            }

        query['is_default_page'] = False
        for item in catalog.searchResults(query):
            loc = item.getURL()
            date = item.modified
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            if item.portal_type in typesUseViewActionInListings:
                loc += '/view'
            yield {
                'loc': loc,
                'lastmod': lastmod,
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
