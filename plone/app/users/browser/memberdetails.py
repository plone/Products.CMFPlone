# Currently unused.
# This file can be removed when this branch is merged.
# May serve as an example for subclassing the registration form.

from register import RegistrationForm 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from zope.formlib import form
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

class DetailsForm(RegistrationForm):
    """ Form for members to set their own properties """

    label = _(u'heading_member_details_form', default=u'Member details form')
    description = u"Manage your personal information on the site."

    @property
    def form_fields(self):
        """ Currently, we remove email and username fields """
        defaultFields = super(DetailsForm, self).form_fields
        defaultFields = defaultFields.omit('username', 'email', 'mail_me')
        return defaultFields

    @form.action(_(u'label_update', default=u'Update'),
                 validator='validate_update', name=u'update')
    def action_update(self, action, data):
        result = self.handle_update_success(data)
        # Stay on the page
        pass

    def validate_update(self, action, data):
        """ TODO add validation criteria here """
        return 

    def handle_update_success(self, data):
        portal = getUtility(ISiteRoot)
        portal_membership = getToolByName(self.context, 'portal_membership')

        member = portal_membership.getAuthenticatedMember()
        member.setProperties(data)

        IStatusMessage(self.request).addStatusMessage(
            _(u'status_settings_updated',
              default=u"Your personal settings have been saved.",),
            type='info')
        return


