from plone.memoize.view import memoize
from Products.CMFPlone.browser.interfaces import IMainTemplate
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IMainTemplate)
class MainTemplate(BrowserView):
    ajax_template = ViewPageTemplateFile("templates/ajax_main_template.pt")
    main_template = ViewPageTemplateFile("templates/main_template.pt")

    def __call__(self):
        return self.template()

    @property
    @memoize
    def plone_layout(self):
        return getMultiAdapter((self.context, self.request), name="plone_layout")

    @property
    def template(self):
        if self.plone_layout.use_ajax():
            return self.ajax_template
        else:
            return self.main_template

    @property
    def macros(self):
        return self.template.macros
