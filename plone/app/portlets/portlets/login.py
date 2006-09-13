from OFS.SimpleItem import SimpleItem

from zope.interface import Interface, implements
from zope.component import adapts

from zope import schema
from zope.formlib import form

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager

from Acquisition import Explicit, Implicit

from plone.app.portlets.browser.formhelper import NullAddForm, EditForm
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from zope.app.container.contained import Contained

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

class ILoginPortlet(IPortletDataProvider):
    """A portlet which can render a login form.
    """
                               
class LoginPortletAssignment(SimpleItem, Contained):
    implements(ILoginPortlet, IPortletAssignment)

    title = _(u'Login portlet')

    @property
    def available(self):
        return True

    @property
    def data(self):
        return self

    def __repr__(self):
        return '<LoginPortlet>'

class LoginPortletRenderer(Explicit):
    implements(IPortletRenderer)
    adapts(Interface, IBrowserRequest, IBrowserView, 
            IPortletManager, ILoginPortlet)
            
    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request

    def show(self):
        membership = getToolByName(self.context, 'portal_membership')
        if not membership.isAnonymousUser():
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page not in ('login_form', 'join_form')

    def available(self):
        return self.auth() is not None

    def login_form(self):
        url = getToolByName(self.context, 'portal_url')
        return '%s/join_form' % url()
        
    def mail_password_form(self):
        url = getToolByName(self.context, 'portal_url')
        return '%s/mail_password_form' % url()

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
        actions = getToolByName(self.context, 'portal_actions')
        userActions = actions.listFilteredActionsFor(self.context)['user']
        joinAction = [a['url'] for a in userActions if a['id'] == 'join']
        if len(joinAction) > 0:
            return joinAction.pop()
        else:
            return None
            
    def can_register(self):
        registration = getToolByName(self.context, 'portal_registration', None)
        membership = getToolByName(self.context, 'portal_membership')
        if registration is None:
            return False
        return membership.checkPermission('Add portal member', self.context)
    
    def can_request_password(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission('Mail forgotten password', self.context)

    def auth(self):
        acl_users = getToolByName(self.context, 'acl_users')
        return getattr(acl_users, 'credentials_cookie_auth', None)

    def update(self):
        pass

    render = ZopeTwoPageTemplateFile('login.pt')

    def __repr__(self):
        return '<LoginPortletRenderer>'


class LoginPortletAddForm(NullAddForm):

    def create(self):
        return LoginPortletAssignment()