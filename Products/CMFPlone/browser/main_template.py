from plone.base.utils import is_truthy
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.interfaces import IMainTemplate
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.interface import implementer


@implementer(IMainTemplate)
class MainTemplate(BrowserView):
    ajax_template = ViewPageTemplateFile("templates/ajax_main_template.pt")
    main_template = ViewPageTemplateFile("templates/main_template.pt")

    def __call__(self):
        return self.template()

    def is_xhr(self):
        """Check if the current request is an XHR request."""
        return self.request.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

    def use_ajax(self):
        """Check if the current request should use the ajax main template."""

        # if ajax_load is not None:
        if ajax_load := self.request.get("ajax_load", None) is not None:
            # Explicitly set ajax_load takes precedence.
            return is_truthy(ajax_load)

        # Use the ajax main template if enabled and if we have an XHR request.
        registry = getUtility(IRegistry)
        use_ajax = self.is_xhr() and registry.get("plone.use_ajax", False)
        return use_ajax

    @property
    def template(self):
        if self.use_ajax():
            return self.ajax_template
        else:
            return self.main_template

    @property
    def macros(self):
        return self.template.macros
