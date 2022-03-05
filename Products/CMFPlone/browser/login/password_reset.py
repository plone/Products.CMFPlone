from AccessControl.SecurityManagement import getSecurityManager
from DateTime import DateTime
from email.header import Header
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPasswordResetToolView
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.PasswordResetTool import ExpiredRequestError
from Products.CMFPlone.PasswordResetTool import InvalidRequestError
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import safeToInt
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PlonePAS.events import UserInitialLoginInEvent
from Products.PlonePAS.events import UserLoggedInEvent
from Products.PluggableAuthService.interfaces.plugins import ICredentialsUpdatePlugin  # noqa
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPasswordResetToolView)
class PasswordResetToolView(BrowserView):

    @view.memoize_contextless
    def portal_state(self):
        """ return portal_state of plone.app.layout
        """
        return getMultiAdapter((self.context, self.request),
                               name="plone_portal_state")

    def encode_mail_header(self, text):
        """ Encodes text into correctly encoded email header """
        return Header(safe_unicode(text), 'utf-8')

    def encoded_mail_sender(self):
        """ returns encoded version of Portal name <portal_email> """
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_ = mail_settings.email_from_name
        mail = mail_settings.email_from_address
        return '"{}" <{}>'.format(self.encode_mail_header(from_).encode(), mail)

    def registered_notify_subject(self):
        portal_name = self.portal_state().portal_title()
        return translate(
            _(
                'mailtemplate_user_account_info',
                default='User Account Information for ${portal_name}',
                mapping={'portal_name': safe_unicode(portal_name)},
            ),
            context=self.request,
        )

    def mail_password_subject(self):
        return translate(
            _(
                'mailtemplate_subject_resetpasswordrequest',
                default='Password reset request',
            ),
            context=self.request,
        )

    def construct_url(self, randomstring):
        return '{}/passwordreset/{}'.format(
            self.portal_state().navigation_root_url(), randomstring)

    def expiration_timeout(self):
        pw_tool = getToolByName(self.context, 'portal_password_reset')
        timeout = int(pw_tool.getExpirationTimeout() or 0)
        return timeout * 24  # timeout is in days, but templates want in hours.


@implementer(IPublishTraverse)
class PasswordResetView(BrowserView):
    """ """

    invalid = ViewPageTemplateFile('templates/pwreset_invalid.pt')
    expired = ViewPageTemplateFile('templates/pwreset_expired.pt')
    finish = ViewPageTemplateFile('templates/pwreset_finish.pt')
    form = ViewPageTemplateFile('templates/pwreset_form.pt')
    subpath = None

    def _auto_login(self, userid, password):
        context = self.context
        aclu = getToolByName(context, 'acl_users')
        for name, plugin in aclu.plugins.listPlugins(ICredentialsUpdatePlugin):
            plugin.updateCredentials(
                self.request,
                self.request.response,
                userid,
                password
            )

        member = get_member_by_login_name(context, userid, False)

        if member:
            user = member.getUser()
        else:
            # Fallback in case we cannot find a user
            # with the given userid
            user = getSecurityManager().getUser()

        default = DateTime('2000/01/01')
        login_time = user.getProperty('login_time', default)
        if login_time == default:
            notify(UserInitialLoginInEvent(user))
        else:
            notify(UserLoggedInEvent(user))

        IStatusMessage(self.request).addStatusMessage(
            _(
                'password_reset_successful',
                default='Password reset successful, '
                        'you are logged in now!',
            ),
            'info',
        )
        url = INavigationRoot(self.context).absolute_url()
        self.request.response.redirect(url)
        return

    def _reset_password(self, pw_tool, randomstring):
        state = self.getErrors()
        if state:
            return self.form()
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
        registry = getUtility(IRegistry)
        if registry.get('plone.autologin_after_password_reset', False):
            return self._auto_login(userid, password)
        return self.finish()

    def __call__(self):
        if self.subpath:
            # Try traverse subpath first:
            randomstring = self.subpath[0]
        else:
            randomstring = self.request.get('key', None)

        pw_tool = getToolByName(self.context, 'portal_password_reset')
        if self.request.method == 'POST':
            return self._reset_password(pw_tool, randomstring)
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
            state['userid'] = _(
                'This field is required, please provide some information.',
            )
        if state:
            state['status'] = 'failure'
            state['portal_status_message'] = _(
                'Please correct the indicated errors.',
            )
        return state

    def login_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name="plone_portal_state")
        return '{}/login?__ac_name={}'.format(
            portal_state.navigation_root_url(),
            self.request.form.get('userid', ''))

    def expiration_timeout(self):
        pw_tool = getToolByName(self.context, 'portal_password_reset')
        timeout = int(pw_tool.getExpirationTimeout() or 0)
        return timeout * 24  # timeout is in days, but templates want in hours.


class ExplainPWResetToolView(BrowserView):
    """ """

    def timeout_days(self):
        return self.context.getExpirationTimeout()

    def user_check(self):
        return self.context._user_check and 'checked' or None

    @property
    def stats(self):
        """Return a dictionary like so:
            {"open":3, "expired":0}
        about the number of open and expired reset requests.
        """
        # count expired reset requests by creating a list of it
        bad = len([1 for expiry in self.context._requests.values()
                   if self.context.expired(expiry)])
        # open reset requests are all requests without the expired ones
        good = len(self.context._requests) - bad
        return {"open": good, "expired": bad}

    def __call__(self):
        if self.request.method == 'POST':
            timeout_days = safeToInt(self.request.get('timeout_days'), 7)
            self.context.setExpirationTimeout(timeout_days)
            self.context._user_check = bool(
                self.request.get('user_check', False),
            )
        return self.index()
