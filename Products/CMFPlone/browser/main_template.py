from plone.base.utils import is_truthy
from Products.CMFPlone.browser.interfaces import IMainTemplate
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IMainTemplate)
class MainTemplate(BrowserView):
    ajax_template = ViewPageTemplateFile("templates/ajax_main_template.pt")
    main_template = ViewPageTemplateFile("templates/main_template.pt")

    def __call__(self):
        return self.template()

    @property
    def template(self):
        # Directly query the request object, which also includes the form.
        if is_truthy(self.request.get("ajax_load")):
            return self.ajax_template
        else:
            return self.main_template

    @property
    def macros(self):
        return self.template.macros
