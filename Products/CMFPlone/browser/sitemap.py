from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implementer

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.browser.interfaces import ISitemapView


@implementer(ISitemapView)
class SitemapView(BrowserView):

    item_template = ViewPageTemplateFile('templates/sitemap-item.pt')

    def createSiteMap(self):
        context = aq_inner(self.context)
        view = getMultiAdapter((context, self.request),
                               name='sitemap_builder_view')
        data = view.siteMap()
        return self._renderLevel(children=data.get('children', []))

    def _renderLevel(self, children=[], level=2):
        output = ''
        for node in children:
            output += '<li class="navTreeItem visualNoMarker">\n'
            output += self.item_template(node=node)
            children = node.get('children', [])
            if len(children):
                output += \
                    '<ul class="navTree navTreeLevel%d">\n%s\n</ul>\n' % (
                        level, self._renderLevel(children, level + 1))
            output += '</li>\n'

        return output
