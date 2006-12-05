from zope.formlib import form

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.formlib.formbase import EditForm


class ControlPanelForm(EditForm):
    """A simple form to be used as a basis for control panel screens."""

    template = ZopeTwoPageTemplateFile('control-panel.pt')

    def __init__(self, *args, **kwargs):
        EditForm.__init__(self, *args, **kwargs)

    @form.action(_(u'Save'))
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
        else:
            self.status = _("No changes done.")

    @form.action(_(u'Cancel'))
    def handle_cancel_action(self, action, data):
        self.status = _("Changes canceled.")
        return

