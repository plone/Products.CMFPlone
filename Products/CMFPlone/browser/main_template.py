from zope.interface import implements

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.browser.interfaces import IMainTemplate


class MainTemplate(BrowserView):
    implements(IMainTemplate)

    ajax_template = ViewPageTemplateFile('templates/ajax_main_template.pt')
    main_template = ViewPageTemplateFile('templates/main_template.pt')

    def __call__(self):
        return self.template()

    @property
    def template(self):
        if self.request.form.get('ajax_load'):
            return self.ajax_template
        else:
            return self.main_template

    @property
    def macros(self):
        return self.template.macros
