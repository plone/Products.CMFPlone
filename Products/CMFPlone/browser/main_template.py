from Products.CMFPlone.browser.interfaces import IMainTemplate
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IMainTemplate)
class MainTemplate(BrowserView):

    ajax_template_name = 'templates/ajax_main_template.pt'
    main_template_name = 'templates/main_template.pt'

    def __call__(self):
        return ViewPageTemplateFile(self.template_name)

    @property
    def template_name(self):
        if self.request.form.get('ajax_load'):
            return self.ajax_template_name
        else:
            return self.main_template_name

    @property
    def macros(self):
        # Reinstanciating the templatefile is a workaround for
        # https://github.com/plone/Products.CMFPlone/issues/2666
        # Without this a inifite recusion in a template
        # (i.e. a template that calls its own view)
        # kills the instance instead of raising a RecursionError.
        return ViewPageTemplateFile(self.template_name).macros
