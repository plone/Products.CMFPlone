from AccessControl import Unauthorized

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import getToolByName, pretty_title_or_id
from Products.statusmessages.interfaces import IStatusMessage

from z3c.form import form, field, button

from zope.component import getUtility, getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from urllib import quote_plus

from interfaces import IAuthorFeedbackForm


class AuthorFeedbackForm(form.Form):

    fields = field.Fields(IAuthorFeedbackForm)
    ignoreContext = True

    @button.buttonAndHandler(_(u'label_send', default='Send'),
                             name='send')
    def handle_send(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).addStatusMessage(
                self.formErrorsMessage,
                type=u'error'
            )

            return


@implementer(IPublishTraverse)
class AuthorView(BrowserView):

    template = ViewPageTemplateFile('templates/author.pt')

    def __init__(self, context, request):
        super(AuthorView, self).__init__(context, request)

        self.username = None

        self.portal_properties = getUtility(
            IPropertiesTool
        )

        self.portal_catalog = getToolByName(
            self.context, 'portal_catalog'
        )

        # XXX: getUtility call does not work.
        self.membership_tool = getToolByName(
            self.context, 'portal_membership'
        )

        self.portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )

        self.feedback_form = AuthorFeedbackForm(
            self.context, self.request
        )
        self.feedback_form.update()

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

    @property
    def member_info(self):
        current_member = self.portal_state.member()
        return {
            'url': quote_plus(current_member.getId()),
            'email': current_member.getProperty('email')
        }

    @property
    def author_content(self):
        results = []

        plone_view = self.context.restrictedTraverse(
            '@@plone'
        )

        brains = self.portal_catalog.searchResults(
            Creator=self.username,
            sort_on='created',
            sort_order='reverse'
        )

        for brain in brains[:10]:
            results.append({
                'title': pretty_title_or_id(
                    self, brain
                ),
                'date': plone_view.toLocalizedTime(
                    brain.Date
                ),
                'url': brain.getURL()
            })

        return results

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
