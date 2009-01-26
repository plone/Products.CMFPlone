from AccessControl import getSecurityManager
from Acquisition import aq_inner

from zope.component import getMultiAdapter, queryMultiAdapter
from plone.memoize.instance import memoize

from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import log
import logging


class DocumentActionsViewlet(ViewletBase):
    def update(self):
        super(DocumentActionsViewlet, self).update()

        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.actions = self.context_state.actions().get('document_actions', None)

    index = ViewPageTemplateFile("document_actions.pt")


class DocumentBylineViewlet(ViewletBase):
    def update(self):
        super(DocumentBylineViewlet, self).update()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.tools = getMultiAdapter((self.context, self.request),
                                     name='plone_tools')

    @memoize
    def show(self):
        properties = self.tools.properties()
        site_properties = getattr(properties, 'site_properties')
        anonymous = self.portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty('allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout

    @memoize
    def locked_icon(self):
        if not getSecurityManager().checkPermission('Modify portal content',
                                                    self.context):
            return ""

        locked = False
        lock_info = queryMultiAdapter((self.context, self.request),
                                      name='plone_lock_info')
        if lock_info is not None:
            locked = lock_info.is_locked()
        else:
            context = aq_inner(self.context)
            lockable = getattr(context.aq_explicit, 'wl_isLocked', None) is not None
            locked = lockable and context.wl_isLocked()

        if not locked:
            return ""

        portal = self.portal_state.portal()
        icon = portal.restrictedTraverse('lock_icon.gif')
        return icon.tag(title='Locked')

    @memoize
    def creator(self):
        return self.context.Creator()

    @memoize
    def author(self):
        membership = self.tools.membership()
        return membership.getMemberInfo(self.creator())

    @memoize
    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

    @memoize
    def isExpired(self):
        portal = self.portal_state.portal()
        return portal.restrictedTraverse('isExpired')(self.context)

    @memoize
    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        try:
            return util.ulocalized_time(time, long_format, time_only, self.context,
                                        domain='plonelocales')
        except TypeError: # Plone 3.1 has no time_only argument
            return util.ulocalized_time(time, long_format, self.context,
                                        domain='plonelocales')

    index = ViewPageTemplateFile("document_byline.pt")


class WorkflowHistoryViewlet(ViewletBase):
    def update(self):
        super(WorkflowHistoryViewlet, self).update()
        self.tools = getMultiAdapter((self.context, self.request),
                                     name='plone_tools')
    @memoize
    def workflowHistory(self):
        """Return workflow history of this context.

        Taken from plone_scripts/getWorkflowHistory.py
        """
        workflow = self.tools.workflow()
        membership = self.tools.membership()

        history = []

        # check if the current user has the proper permissions
        if (membership.checkPermission('Request review', self.context) or
            membership.checkPermission('Review portal content', self.context)):
            try:
                # get total history
                review_history = workflow.getInfoFor(self.context, 'review_history')

                # filter out the irrelevant stuff
                review_history = [r for r in review_history if r['action']]
                for r in review_history:
                    r['transition_title'] = workflow.getTitleForTransitionOnType(r['action'],
                                                                                 self.context.portal_type)
                    actorid = r['actor']
                    r['actorid'] = actorid
                    if actorid is None:
                        # action performed by an anonymous user
                        r['actor'] = {'username': _(u'label_anonymous_user', default=u'Anonymous User')}
                        r['actor_home'] = ''
                    else:
                        r['actor'] = membership.getMemberInfo(actorid)
                        if r['actor'] is not None:
                            r['actor_home'] = self.site_url + '/author/' + actorid
                        else:
                            # member info is not available
                            # the user was probably deleted
                            r['actor_home'] = ''
                history = review_history
                history.reverse()

            except WorkflowException:
                log( 'plone.app.layout.viewlets.content: '
                     '%s has no associated workflow' % self.context.absolute_url(), severity=logging.DEBUG)

        return history

    index = ViewPageTemplateFile("review_history.pt")
