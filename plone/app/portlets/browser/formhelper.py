from zope.component import getMultiAdapter
from zope.formlib import form
import zope.event
import zope.lifecycleevent

from Acquisition import aq_parent, aq_inner
from Products.Five.formlib.formbase import AddFormBase, EditFormBase

class AddForm(AddFormBase):
    """A base add form for portlets.
    
    Sub-classes should define create() and set the form_fields class variable.
    """
    
    def nextURL(self):
        addview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(addview))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@manage-portlets'
    
    @form.action("Save")
    def handle_save_action(self, action, data):
        self.createAndAdd(data)
    
    @form.action("Cancel", validator=lambda *args, **kwargs: None)
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
            return ''

class EditForm(EditFormBase):
    """An edit form for portlets.
    """
    
    def nextURL(self):
        portlet = aq_inner(self.context)
        context = aq_parent(portlet)
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@manage-portlets'
    
    @form.action("Save", condition=form.haveInputWidgets)
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self.context))
            self.status = "Changes saved"
        else:
            self.status = "No changes"
            
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
            return ''
            
    @form.action("Cancel", validator=lambda *args, **kwargs: None)
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
            return ''