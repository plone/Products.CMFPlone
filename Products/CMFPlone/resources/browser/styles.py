from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IResourceRegistry
from urlparse import urlparse


class ScriptsView(ViewletBase):
    """ Information for script rendering. """

    def registry(self):
        registry = getUtility(IRegistry)
        return registry.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")

    def scripts(self):
        resources = self.registry()

        result = []
        for resource in resources:
            if script.js:
                url = urlparse(script.js)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (self.portal_url, script.js)
                else:
                    src = "%s" % (script.js)

            data = {'conditionalcomment' : script.getConditionalcomment(),
                    'src': src}
            result.append(data)
        return result


class StylesView(ViewletBase):
    """ Information for style rendering. """

    def registry(self):
        return getToolByName(aq_inner(self.context), 'portal_css')

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def styles(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        styles = registry.getEvaluatedResources(context)
        skinname = url_quote(self.skinname())
        result = []
        for style in styles:
            rendering = style.getRendering()
            if style.isExternalResource():
                src = "%s" % style.getId()
            else:
                src = "%s/%s/%s" % (registry_url, skinname, style.getId())
            if style.getCompile():
                src = "%s/@@compile_less?url=%s" % (registry_url, url_quote(src))
                if style.getDeps():
                    deps = style.getDeps().split(',')
                    for dep in deps:
                        # Get the resource compiled and add to result
                        # Check if its already in the result
                        pass
            if rendering == 'link':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'rel': style.getRel() if not style.getCompile() else 'stylesheet/css',
                        'title': style.getTitle(),
                        'conditionalcomment' : style.getConditionalcomment(),
                        'src': src}
            elif rendering == 'import':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment' : style.getConditionalcomment(),
                        'src': src}
            elif rendering == 'inline':
                content = registry.getInlineResource(style.getId(), context)
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment' : style.getConditionalcomment(),
                        'content': content}
            else:
                raise ValueError("Unkown rendering method '%s' for style '%s'" % (rendering, style.getId()))
            result.append(data)
        return result
