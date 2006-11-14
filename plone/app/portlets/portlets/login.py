from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

class ILoginPortlet(IPortletDataProvider):
    """A portlet which can render a login form.
    """

class Assignment(base.Assignment):
    implements(ILoginPortlet)

    title = _(u'Login portlet')

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        
        self.membership = getToolByName(self.context, 'portal_membership')
        self.actions = getToolByName(self.context, 'portal_actions')
        self.registration = getToolByName(self.context, 'portal_registration', None)
        
        self.portal_url = getToolByName(self.context, 'portal_url')()

    def show(self):
        if not self.membership.isAnonymousUser():
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page not in ('login_form', 'join_form')

    def available(self):
        return self.auth() is not None

    def login_form(self):
        return '%s/login_form' % self.portal_url

    def mail_password_form(self):
        return '%s/mail_password_form' % portal_url

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

    def persist_cookie(self):
        auth = self.auth()
        persist = False
        if auth is not None:
            persist = getattr(auth, 'persist_cookie', None)
        return persist

    def join_action(self):
        userActions = self.actions.listFilteredActionsFor(self.context)['user']
        joinAction = [a['url'] for a in userActions if a['id'] == 'join']
        if len(joinAction) > 0:
            return joinAction.pop()
        else:
            return None

    def can_register(self):
        if self.registration is None:
            return False
        return self.membership.checkPermission('Add portal member', self.context)

    def can_request_password(self):
        return self.membership.checkPermission('Mail forgotten password', self.context)

    def auth(self, _marker=[]):
        auth = getattr(self, '_auth', _marker)
        if auth is _marker:
            acl_users = getToolByName(self.context, 'acl_users')
            auth = self._auth = getattr(acl_users, 'credentials_cookie_auth', None)
        return auth

    def update(self):
        pass

    render = ZopeTwoPageTemplateFile('login.pt')

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()