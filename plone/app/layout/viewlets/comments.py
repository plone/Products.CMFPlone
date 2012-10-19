from Acquisition import aq_inner, aq_base
from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed

from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter


class CommentsViewlet(ViewletBase):
    index = ViewPageTemplateFile('comments.pt')

    def update(self):
        super(CommentsViewlet, self).update()
        self.portal_discussion = getToolByName(self.context, 'portal_discussion', None)
        self.portal_membership = getToolByName(self.context, 'portal_membership', None)

    def can_reply(self):
        return getSecurityManager().checkPermission('Reply to item', aq_inner(self.context))

    def is_discussion_allowed(self):
        if self.portal_discussion is None:
            return False
        else:
            return self.portal_discussion.isDiscussionAllowedFor(aq_inner(self.context))

    def get_replies(self):
        replies = []

        context = aq_inner(self.context)
        pd = self.portal_discussion

        # cut out early if there's no talkback attribute, to avoid having
        # getDiscussionFor implicitly create one unnecessarily
        if getattr(aq_base(context), 'talkback', None) is None:
            return []

        def getRs(obj, replies, counter):
            rs = pd.getDiscussionFor(obj).getReplies()
            if len(rs) > 0:
                rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                for r in rs:
                    replies.append({'depth':counter, 'object':r})
                    getRs(r, replies, counter=counter + 1)

        try:
            getRs(context, replies, 0)
        except DiscussionNotAllowed:
            # We tried to get discussions for an object that has not only
            # discussions turned off but also no discussion container.
            return []
        return replies

    def is_anonymous(self):
        return self.portal_state.anonymous()

    def login_url(self):
        """Return the URL of the 'login' portal_action if there is one. Otherwise, return None."""
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')
        for action in context_state.actions('user'):
            if action.get('id') == 'login':
                return action.get('url')

    def can_manage(self):
        return getSecurityManager().checkPermission('Manage portal', aq_inner(self.context))

    def member_info(self, creator):
        if self.portal_membership is None:
            return None
        else:
            return self.portal_membership.getMemberInfo(creator)

    def format_time(self, time):
        context = aq_inner(self.context)
        util = getToolByName(context, 'translation_service')
        return util.ulocalized_time(time, long_format=1, time_only=None, context=context, domain='plonelocales')
