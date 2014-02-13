from AccessControl import Unauthorized

from Products.CMFPlone.interfaces import IPropertiesTool
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PlonePAS.interfaces.membership import IMembershipTool

from zope.component import getUtility, getMultiAdapter

from urllib import unquote_plus


class AuthorView(BrowserView):

    template = ViewPageTemplateFile('templates/author.pt')

    def __init__(self, context, request):
        super(AuthorView, self).__init__(context, request)

        self.portal_properties = getUtility(IPropertiesTool)
        self.membership_tool = getUtility(IMembershipTool)

        self.portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )

    @property
    def anonymous(self):
        return self.portal_state.anonymous()

    @property
    def author(self):
        if len(self.request.traverse_subpath) > 0:
            username = unquote_plus(self.request.traverse_subpath[0])
        else:
            username = self.request.get('author', None)

        authorinfo = self.membership_tool.getMemberInfo(username)
        portrait = self.membership_tool.getPersonalPortrait(username)

        if not authorinfo or not portrait:
            return {}

        return {
            'authorinfo': authorinfo,
            'portrait': portrait
        }

    def __call__(self):
        site_properties = self.portal_properties.site_properties
        allow_anonymous_view_about = site_properties.getProperty(
            'allowAnonymousViewAbout', True
        )

        if self.anonymous and not allow_anonymous_view_about:
            raise Unauthorized()

        return self.template()


