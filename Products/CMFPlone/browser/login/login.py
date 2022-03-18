from DateTime import DateTime
from plone.app.users.browser.passwordpanel import PasswordPanel
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IForcePasswordChange
from Products.CMFPlone.interfaces import IInitialLogin
from Products.CMFPlone.interfaces import ILoginForm
from Products.CMFPlone.interfaces import ILoginFormSchema
from Products.CMFPlone.interfaces import IRedirectAfterLogin
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from urllib import parse
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer


# TODO: Scale down this list now that we've removed a lot of
# templates.
LOGIN_TEMPLATE_IDS = [
    'localhost',
    'logged-out',
    'logged_in',
    'login',
    'login_failed',
    'login_form',
    'login_password',
    'login_success',
    'logout',
    'mail_password',
    'mail_password_form',
    'member_search_results',
    'pwreset_finish',
    'passwordreset',
    'register',
    'registered',
    'require_login',
]


@implementer(ILoginForm)
class LoginForm(form.EditForm):
    """ Implementation of the login form """

    fields = field.Fields(ILoginFormSchema)

    id = 'LoginForm'
    label = _('label_log_in', default='Log in')

    ignoreContext = True
    prefix = ''

    def render(self):
        registry = queryUtility(IRegistry)
        ext_login_url = registry['plone.external_login_url']
        if ext_login_url:
            return self._handle_external_login(ext_login_url)
        return self.index()

    def _handle_external_login(self, url):
        """Handle login on this portal where login is external."""
        next_ = self.request.get('next', None)
        came_from = self.request.get('came_from')
        urlparts = [part for part in parse.urlparse(url)]
        qs = dict(parse.parse_qsl(urlparts[4]))
        portal_url = getToolByName(self.context, 'portal_url')
        if next_ is not None and not portal_url.isURLInPortal(next_):
            next_ = None
        if next_ is not None:
            qs['next'] = next_
        if came_from:
            qs['came_from'] = came_from
        urlparts[4] = parse.urlencode(qs)
        self.request.response.redirect(parse.urlunparse(urlparts))

    def _get_auth(self):
        try:
            return self.context.acl_users.credentials_cookie_auth
        except AttributeError:
            try:
                return self.context.cookie_authentication
            except AttributeError:
                pass

    def updateWidgets(self):
        super().updateWidgets(prefix='')

        auth = self._get_auth()

        if auth:
            widgetname_login = auth.get('name_cookie', '__ac_name')
            widgetname_password = auth.get('pw_cookie', '__ac_password')
        else:
            widgetname_login = '__ac_name'
            widgetname_password = '__ac_password'

        self.widgets['ac_name'].name = widgetname_login
        self.widgets['ac_name'].id = widgetname_login
        self.widgets['ac_password'].name = widgetname_password
        self.widgets['ac_password'].id = widgetname_password

        if self.use_email_as_login():
            self.widgets['ac_name'].label = _('label_email',
                                                   default='Email')
        self.widgets['came_from'].mode = HIDDEN_MODE
        self.widgets['came_from'].value = self.get_came_from()

    def get_came_from(self):
        came_from = self.request.get('came_from', None)
        if not came_from:
            came_from = self.request.get('HTTP_REFERER', None)
            if not came_from:
                return
        url_tool = getToolByName(self.context, 'portal_url')
        if not url_tool.isURLInPortal(came_from):
            return
        came_from_path = parse.urlparse(came_from)[2].split('/')
        for login_template_id in LOGIN_TEMPLATE_IDS:
            if login_template_id in came_from_path:
                return
        return came_from

    def updateActions(self):
        super().updateActions()
        self.actions['login'].addClass('btn-primary')

    def _post_login(self):
        membership_tool = getToolByName(self.context, 'portal_membership')
        member = membership_tool.getAuthenticatedMember()
        must_change_password = member.getProperty('must_change_password', 0)
        login_time = member.getProperty('login_time', '2000/01/01')
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        is_initial_login = login_time == DateTime('2000/01/01')

        membership_tool.loginUser(self.request)
        if is_initial_login:
            self.handle_initial_login()

        if must_change_password:
            self.force_password_change()
        return is_initial_login

    @button.buttonAndHandler(_('Log in'), name='login')
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        membership_tool = getToolByName(self.context, 'portal_membership')
        status_msg = IStatusMessage(self.request)
        if membership_tool.isAnonymousUser():
            self.request.response.expireCookie('__ac', path='/')
            if self.use_email_as_login():
                status_msg.addStatusMessage(
                    _(
                        'Login failed. Both email address and password are '
                        'case sensitive, check that caps lock is not enabled.'
                    ),
                    'error',
                )
            else:
                status_msg.addStatusMessage(
                    _(
                        'Login failed. Both login name and password are case '
                        'sensitive, check that caps lock is not enabled.'
                    ),
                    'error',
                )
            return

        is_initial_login = self._post_login()
        status_msg.addStatusMessage(
            _(
                'you_are_now_logged_in',
                default='Welcome! You are now logged in.',
            ),
            'info'
        )

        came_from = data.get('came_from', None)
        self.redirect_after_login(came_from, is_initial_login)

    def handle_initial_login(self):
        handler = queryMultiAdapter(
            (self.context, self.request),
            IInitialLogin,
        )
        if handler:
            handler()

    def force_password_change(self):
        handler = queryMultiAdapter(
            (self.context, self.request),
            IForcePasswordChange,
        )
        if handler:
            handler()

    def redirect_after_login(self, came_from=None, is_initial_login=False):
        adapter = queryMultiAdapter(
            (self.context, self.request),
            IRedirectAfterLogin
        )
        if adapter:
            came_from = adapter(came_from, is_initial_login)
        if not came_from:
            came_from = self.context.absolute_url()

        self.request.response.redirect(came_from)

    def self_registration_enabled(self):
        registry = queryUtility(IRegistry)
        security_settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone'
        )
        return security_settings.enable_self_reg

    def use_email_as_login(self):
        registry = queryUtility(IRegistry)
        security_settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone'
        )
        return security_settings.use_email_as_login


class FailsafeLoginForm(LoginForm):

    def render(self):
        return self.index()


class RequireLoginView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state',
        )
        portal = portal_state.portal()
        if portal_state.anonymous():
            url = f'{portal.absolute_url():s}/login'
            came_from = self.request.get('came_from', None)
            if came_from:
                url += '?came_from={:s}'.format(parse.quote(came_from))
        else:
            url = f'{portal.absolute_url():s}/insufficient-privileges'

        self.request.response.redirect(url)


class InsufficientPrivilegesView(BrowserView):

    def request_url(self):
        return self.request.get('came_from')


class InitialLoginPasswordChange(PasswordPanel):

    def render(self):
        return self.index()

    @button.buttonAndHandler(
        _('label_change_password', default='Change Password'),
        name='reset_passwd',
    )
    def action_reset_passwd(self, action):
        super().action_reset_passwd(
            self, action)
        if not action.form.widgets.errors:
            self.request.response.redirect(self.context.portal_url())


class ForcedPasswordChange(PasswordPanel):

    def render(self):
        return self.index()

    @button.buttonAndHandler(
        _('label_change_password', default='Change Password'),
        name='reset_passwd',
    )
    def action_reset_passwd(self, action):
        super().action_reset_passwd(self, action)
        if not action.form.widgets.errors:
            membership_tool = getToolByName(self.context, 'portal_membership')
            member = membership_tool.getAuthenticatedMember()
            member.setProperties(must_change_password=0)
            self.request.response.redirect(self.context.portal_url())
