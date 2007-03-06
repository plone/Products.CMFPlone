from urllib import quote as url_quote

from zope.interface import implements
from zope.component import getUtility
from zope.component import queryUtility
from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager
from Products.CMFCore.interfaces import IDiscussionTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed
from Products.CMFPlone.interfaces import ITranslationServiceTool
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase

class CommentsViewlet(ViewletBase):
    """ Base class with common functions for link viewlets.
    """    
    render = ViewPageTemplateFile('comments.pt')

    def update(self):
        self.portal_discussion = queryUtility(IDiscussionTool)
        self.portal_membership = queryUtility(IMembershipTool)

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
        container = aq_parent(context)
        pd = self.portal_discussion
        
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
        
    def login_action(self):
        return '%s/login_form?came_from=%s' % (self.portal_url, url_quote(self.request.get('URL', '')),)
        
    def can_manage(self):
        return getSecurityManager().checkPermission('Manage portal', aq_inner(self.context))
        
    def member_info(self, creator):
        if self.portal_membership is None:
            return None
        else:
            return self.portal_membership.getMemberInfo(creator)
            
    def format_time(self, time):
        context = aq_inner(self.context)
        util = getUtility(ITranslationServiceTool)
        return util.ulocalized_time(time, 1, context, domain='plonelocales')