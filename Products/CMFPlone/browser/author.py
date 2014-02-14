from AccessControl import Unauthorized

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.utils import getToolByName

from zope.component import getUtility, getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from urllib import unquote_plus


@implementer(IPublishTraverse)
class AuthorView(BrowserView):

    template = ViewPageTemplateFile('templates/author.pt')

    def __init__(self, context, request):
        super(AuthorView, self).__init__(context, request)

        self.username = None
        self.portal_properties = getUtility(IPropertiesTool)

        # XXX: getUtility call does not work.
        self.membership_tool = getToolByName(
            self.context, 'portal_membership'
        )

        self.portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )

    def publishTraverse(self, request, name):
        request['TraversalRequestNameStack'] = []

        self.username = name

        return self

    @property
    def is_anonymous(self):
        return self.portal_state.anonymous()

    @property
    def is_owner(self):
        current_member = self.portal_state.member()
        return current_member.getId() == self.username

    @property
    def author(self):
        username = self.username

        if not username:
            return {}

        authorinfo = self.membership_tool.getMemberInfo(username)
        portrait = self.membership_tool.getPersonalPortrait(username)

        if not authorinfo or not portrait:
            return {}

        return {
            'info': authorinfo,
            'portrait': portrait
        }

    def home_folder(self, username):
        membership_tool = self.membership_tool
        return membership_tool.getHomeFolder(id=username)

    def __call__(self):
        site_properties = self.portal_properties.site_properties
        allow_anonymous_view_about = site_properties.getProperty(
            'allowAnonymousViewAbout', True
        )

        if self.is_anonymous and not allow_anonymous_view_about:
            raise Unauthorized()

        return self.template()
