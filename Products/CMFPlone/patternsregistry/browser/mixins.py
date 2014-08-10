from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote



class LessMixinsWeb(BrowserView):

    def registry(self):
        return getToolByName(aq_inner(self.context), 'portal_css')

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def __call__(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        skinname = url_quote(self.skinname())
        results = [r.copy() for r in registry.getResources() if r.getEnabled()]
        chain_css = ""
        for result in results:
            if result.getComponent():
                chain_css += '@%s: \'%s/%s/%s\';\n' % (result.getComponent().replace('.','-'), registry_url, skinname, result.getId())
        self.request.response.setHeader("Content-Type", "stylesheet/less")

        return """
@pathPrefix: '++resource++plonejs/';
@plonePrefix: '++resource++';
%s""" % chain_css