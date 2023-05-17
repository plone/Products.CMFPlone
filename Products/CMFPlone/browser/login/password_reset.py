from .utils import has_logged_in
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from email.header import Header
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IInitialLogin
from plone.base.interfaces import IPasswordResetToolView
from plone.base.interfaces import IRedirectAfterLogin
from plone.base.interfaces.controlpanel import IMailSchema
from plone.base.utils import safe_text
from plone.base.utils import safeToInt
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PasswordResetTool import ExpiredRequestError
from Products.CMFPlone.PasswordResetTool import InvalidRequestError
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import ICredentialsUpdatePlugin
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPasswordResetToolView)
class PasswordResetToolView(BrowserView):
    @view.memoize_contextless
    def portal_state(self):
        """return portal_state of plone.app.layout"""
        return getMultiAdapter((self.context, self.request), name="plone_portal_state")

    def encode_mail_header(self, text):
        """Encodes text into correctly encoded email header"""
        return Header(safe_text(text), "utf-8")

    def encoded_mail_sender(self):
        """returns encoded version of Portal name <portal_email>"""
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_ = mail_settings.email_from_name
        mail = mail_settings.email_from_address
        return f'"{self.encode_mail_header(from_).encode()}" <{mail}>'

    def registered_notify_subject(self):
        portal_name = self.portal_state().portal_title()
        return translate(
            _(
                "mailtemplate_user_account_info",
                default="User Account Information for ${portal_name}",
                mapping={"portal_name": safe_text(portal_name)},
            ),
            context=self.request,
        )

    def mail_password_subject(self):
        return translate(
            _(
                "mailtemplate_subject_resetpasswordrequest",
                default="Password reset request",
            ),
            context=self.request,
        )

    def construct_url(self, randomstring):
        return "{}/passwordreset/{}".format(
            self.portal_state().navigation_root_url(), randomstring
        )

    def expiration_timeout(self):
        pw_tool = getToolByName(self.context, "portal_password_reset")
        timeout = int(pw_tool.getExpirationTimeout() or 0)
        return timeout * 24  # timeout is in days, but templates want in hours.


@implementer(IPublishTraverse)
class PasswordResetView(BrowserView):
    """ """

    invalid = ViewPageTemplateFile("templates/pwreset_invalid.pt")
    expired = ViewPageTemplateFile("templates/pwreset_expired.pt")
    finish = ViewPageTemplateFile("templates/pwreset_finish.pt")
    form = ViewPageTemplateFile("templates/pwreset_form.pt")
    subpath = None

    def _auto_login(self, userid, password):
        context = self.context
        aclu = getToolByName(context, "acl_users")
        for name, plugin in aclu.plugins.listPlugins(ICredentialsUpdatePlugin):
            plugin.updateCredentials(
                self.request, self.request.response, userid, password
            )

        is_initial_login = False

        # Find member by login name or user id.
        # If this fails, then this is strange.
        member = get_member_by_login_name(context, userid, False)
        if not member:
            self.request.response.redirect(self.context.absolute_url())
            IStatusMessage(self.request).addStatusMessage(
                _(
                    "password_reset_failed",
                    default="Password reset failed.",
                ),
                "info",
            )
            return

        user = member.getUser()
        orig_sm = getSecurityManager()
        try:
            newSecurityManager(self.request, user)
            is_initial_login = self._post_login()
            IStatusMessage(self.request).addStatusMessage(
                _(
                    "password_reset_successful",
                    default="Password reset successful, " "you are logged in now!",
                ),
                "info",
            )
            self.redirect_after_login(is_initial_login=is_initial_login)
        finally:
            setSecurityManager(orig_sm)

        return

    def _post_login(self):
        membership_tool = getToolByName(self.context, "portal_membership")
        member = membership_tool.getAuthenticatedMember()
        login_time = member.getProperty("login_time", None)
        is_initial_login = not has_logged_in(login_time)
        membership_tool.loginUser(self.request)
        if is_initial_login:
            self.handle_initial_login()
        return is_initial_login

    def handle_initial_login(self):
        handler = queryMultiAdapter((self.context, self.request), IInitialLogin)
        if handler:
            handler()

    def redirect_after_login(self, came_from=None, is_initial_login=False):
        # Note: for password reset a came_from parameter seems illogical.
        # But let's allow it, to be the same as in login.py.
        # The default implementation does not pass it in though.
        adapter = queryMultiAdapter((self.context, self.request), IRedirectAfterLogin)
        if adapter:
            came_from = adapter(came_from, is_initial_login)
        if not came_from:
            came_from = self.context.absolute_url()

        self.request.response.redirect(came_from)

    def _reset_password(self, pw_tool, randomstring):
        state = self.getErrors()
        if state:
            return self.form()
        userid = self.request.form.get("userid")
        password = self.request.form.get("password")
        try:
            pw_tool.resetPassword(userid, randomstring, password)
        except ExpiredRequestError:
            return self.expired()
        except InvalidRequestError:
            return self.invalid()
        except RuntimeError:
            return self.invalid()
        registry = getUtility(IRegistry)
        if registry.get("plone.autologin_after_password_reset", False):
            return self._auto_login(userid, password)
        return self.finish()

    def __call__(self):
        if self.subpath:
            # Try traverse subpath first:
            randomstring = self.subpath[0]
        else:
            randomstring = self.request.get("key", None)

        pw_tool = getToolByName(self.context, "portal_password_reset")
        if self.request.method == "POST":
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
        if self.request.method != "POST":
            return
        password = self.request.form.get("password")
        password2 = self.request.form.get("password2")
        userid = self.request.form.get("userid")
        reg_tool = getToolByName(self.context, "portal_registration")
        pw_fail = reg_tool.testPasswordValidity(password, password2)
        state = {}
        if pw_fail:
            state["password"] = pw_fail

        # Determine if we're checking userids or not
        pw_tool = getToolByName(self.context, "portal_password_reset")
        if not pw_tool.checkUser():
            return state

        if not userid:
            state["userid"] = _(
                "This field is required, please provide some information.",
            )
        if state:
            state["status"] = "failure"
            state["portal_status_message"] = _("Please correct the indicated errors.")
        return state

    def login_url(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return "{}/login?__ac_name={}".format(
            portal_state.navigation_root_url(), self.request.form.get("userid", "")
        )

    def expiration_timeout(self):
        pw_tool = getToolByName(self.context, "portal_password_reset")
        timeout = int(pw_tool.getExpirationTimeout() or 0)
        return timeout * 24  # timeout is in days, but templates want in hours.


class ExplainPWResetToolView(BrowserView):
    """ """

    def timeout_days(self):
        return self.context.getExpirationTimeout()

    def user_check(self):
        return self.context._user_check and "checked" or None

    @property
    def stats(self):
        """Return a dictionary like so:
            {"open":3, "expired":0}
        about the number of open and expired reset requests.
        """
        # count expired reset requests by creating a list of it
        bad = len(
            [
                1
                for expiry in self.context._requests.values()
                if self.context.expired(expiry)
            ]
        )
        # open reset requests are all requests without the expired ones
        good = len(self.context._requests) - bad
        return {"open": good, "expired": bad}

    def __call__(self):
        if self.request.method == "POST":
            timeout_days = safeToInt(self.request.get("timeout_days"), 7)
            self.context.setExpirationTimeout(timeout_days)
            self.context._user_check = bool(
                self.request.get("user_check", False),
            )
        return self.index()
