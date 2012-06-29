from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base


class ILoginPortlet(IPortletDataProvider):
    """A portlet which can render a login form.
    """


class Assignment(base.Assignment):
    implements(ILoginPortlet)

    title = _(u'label_log_in', default=u'Log in')


class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.membership = getToolByName(self.context, 'portal_membership')

        self.context_state = getMultiAdapter((context, request), name=u'plone_context_state')
        self.portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.pas_info = getMultiAdapter((context, request), name=u'pas_info')

    def show(self):
        if not self.portal_state.anonymous():
            return False
        if not self.pas_info.hasLoginPasswordExtractor():
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page not in ('login_form', '@@register')

    @property
    def available(self):
        return self.auth() is not None and self.show()

    def login_form(self):
        return '%s/login_form' % self.portal_state.portal_url()

    def mail_password_form(self):
        return '%s/mail_password_form' % self.portal_state.portal_url()

    def login_name(self):
        auth = self.auth()
        name = None
        if auth is not None:
            name = getattr(auth, 'name_cookie', None)
        if not name:
            name = '__ac_name'
        return name

    def login_password(self):
        auth = self.auth()
        passwd = None
        if auth is not None:
            passwd = getattr(auth, 'pw_cookie', None)
        if not passwd:
            passwd = '__ac_password'
        return passwd

    def join_action(self):
        context = self.context
        tool = getToolByName(context, 'portal_actions')
        join = tool.listActionInfos(action_chain='user/join', object=context)
        if len(join) > 0:
            return join[0]['url']
        return None

    def can_register(self):
        if getToolByName(self.context, 'portal_registration', None) is None:
            return False
        return self.membership.checkPermission('Add portal member', self.context)

    def can_request_password(self):
        return self.membership.checkPermission('Mail forgotten password', self.context)

    @memoize
    def auth(self, _marker=None):
        if _marker is None:
            _marker = []
        acl_users = getToolByName(self.context, 'acl_users')
        return getattr(acl_users, 'credentials_cookie_auth', None)

    def update(self):
        pass

    render = ViewPageTemplateFile('login.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
