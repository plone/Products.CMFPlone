from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PrefsMainTemplate(BrowserView):
    prefs_main_template_name = "prefsmaintemplate.pt"

    def __call__(self):
        return ViewPageTemplateFile(self.prefs_main_template_name)

    @property
    def macros(self):
        return ViewPageTemplateFile(self.prefs_main_template_name).macros
