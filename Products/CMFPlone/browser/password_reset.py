from zope.interface import implementer
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.PasswordResetTool import ExpiredRequestError
from Products.CMFPlone.PasswordResetTool import InvalidRequestError
from zope.i18n import translate
from zope.publisher.interfaces import IPublishTraverse

from Products.CMFPlone.interfaces import IPasswordResetToolView
from Products.CMFPlone import PloneMessageFactory as _
from email.Header import Header

from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from Products.CMFPlone.interfaces.controlpanel import IMailSchema


@implementer(IPasswordResetToolView)
class PasswordResetToolView(BrowserView):

    @view.memoize_contextless
    def portal_state(self):
        """ return portal_state of plone.app.layout
        """
        return getMultiAdapter((self.context, self.request),
                               name=u"plone_portal_state")

    def encode_mail_header(self, text):
        """ Encodes text into correctly encoded email header """
        return Header(safe_unicode(text), 'utf-8')

    def encoded_mail_sender(self):
        """ returns encoded version of Portal name <portal_email> """
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_ = mail_settings.email_from_name
        mail = mail_settings.email_from_address
        return '"%s" <%s>' % (self.encode_mail_header(from_), mail)

    def registered_notify_subject(self):
        portal_name = self.portal_state().portal_title()
        return translate(_(u"mailtemplate_user_account_info",
                           default=u"User Account Information for ${portal_name}",
                           mapping={'portal_name': safe_unicode(portal_name)}),
                           context=self.request)

    def mail_password_subject(self):
        return translate(_(u"mailtemplate_subject_resetpasswordrequest",
                           default=u"Password reset request"),
                           context=self.request)

    def construct_url(self, randomstring):
        return "%s/passwordreset/%s" % (
            self.portal_state().navigation_root_url(), randomstring)


@implementer(IPublishTraverse)
class PasswordResetView(BrowserView):
    """ """

    invalid = ViewPageTemplateFile('templates/pwreset_invalid.pt')
    expired = ViewPageTemplateFile('templates/pwreset_expired.pt')
    finish = ViewPageTemplateFile('templates/pwreset_finish.pt')
    form = ViewPageTemplateFile('templates/pwreset_form.pt')
    subpath = None

    def __call__(self):
        if self.subpath:
            # Try traverse subpath first:
            randomstring = self.subpath[0]
        else:
            randomstring = self.request.get('key', None)

        pw_tool = getToolByName(self.context, 'portal_password_reset')
        if self.request.method == 'POST':
            userid = self.request.form.get('userid')
            password = self.request.form.get('password')
            try:
                pw_tool.resetPassword(userid, randomstring, password)
            except ExpiredRequestError:
                return self.expired()
            except InvalidRequestError:
                return self.invalid()
            except RuntimeError:
                return self.invalid()
            return self.finish()
        else:
            try:
                pw_tool.verifyKey(randomstring)
            except InvalidRequestError:
                return self.invalid()
            except ExpiredRequestError:
                return self.expired()
            return self.form()

    def publishTraverse(self, request, name):
        if self.subpath is None:
            self.subpath = []
        self.subpath.append(name)
        return self

    def getErrors(self):
        if self.request.method != 'POST':
            return
        password = self.request.form.get('password')
        password2 = self.request.form.get('password2')
        userid = self.request.form.get('userid')
        reg_tool = getToolByName(self.context, 'portal_registration')
        pw_fail = reg_tool.testPasswordValidity(password, password2)
        state = {}
        if pw_fail:
            state['password'] = pw_fail

        # Determine if we're checking userids or not
        pw_tool = getToolByName(self.context, 'portal_password_reset')
        if not pw_tool.checkUser():
            return state

        if not userid:
            state['userid'] = _('This field is required, please provide some information.')
        if state:
            state['status'] = 'failure'
            state['portal_status_message'] = 'Please correct the indicated errors.'
        return state


class ExplainPWResetToolView(BrowserView):
    """ """