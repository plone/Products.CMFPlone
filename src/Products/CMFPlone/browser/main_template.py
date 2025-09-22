from plone.base.utils import is_truthy
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.interfaces import IMainTemplate
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility
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
    @memoize
    def use_ajax(self):
        """Check if we should use some AJAX specifica.
        This is used to load the AJAX main template instead of the regular one.
        """

        # ajax_load request/query parameters which are explicitly set take
        # precedence over automatic AJAX detection.
        if "ajax_load" in self.request:
            return is_truthy(self.request.get("ajax_load", False))

        if not self.plone_layout.is_xhr:
            # Not and ajax request. Use the normal main template.
            return False

        # Automatic AJAX detection needs to be turned on.
        registry = getUtility(IRegistry)
        use_ajax = registry.get("plone.use_ajax_main_template", False)

        # If use_ajax is turned on, use the ajax template.
        return use_ajax

    @property
    def template(self):
        if self.use_ajax:
            return self.ajax_template
        else:
            return self.main_template

    @property
    def macros(self):
        return self.template.macros
