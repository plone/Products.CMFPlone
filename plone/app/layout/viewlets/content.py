from AccessControl import getSecurityManager
from Acquisition import aq_inner

from zope.component import getMultiAdapter, queryMultiAdapter
from plone.memoize.instance import memoize

from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.Permissions import AccessPreviousVersions

from Products.CMFPlone import PloneMessageFactory as _

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import log
import logging


class DocumentActionsViewlet(ViewletBase):
    def update(self):
        super(DocumentActionsViewlet, self).update()

        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.actions = self.context_state.actions('document_actions')

    index = ViewPageTemplateFile("document_actions.pt")


class DocumentBylineViewlet(ViewletBase):
    def update(self):
        super(DocumentBylineViewlet, self).update()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')

    @memoize
    def show(self):
        properties = getToolByName(self.context, 'portal_properties')
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
        membership = getToolByName(self.context, 'portal_membership')
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

    @memoize
    def workflowHistory(self, complete=False):
        """Return workflow history of this context.

        Taken from plone_scripts/getWorkflowHistory.py
        """
        workflow = getToolByName(self.context, 'portal_workflow')
        membership = getToolByName(self.context, 'portal_membership')

        review_history = []

        # check if the current user has the proper permissions
        if (membership.checkPermission('Request review', self.context) or
            membership.checkPermission('Review portal content', self.context)):
            try:
                # get total history
                review_history = workflow.getInfoFor(self.context, 'review_history')

                if not complete:
                    # filter out automatic transitions.
                    review_history = [r for r in review_history if r['action']]
                else:
                    review_history = list(review_history)

                for r in review_history:
                    r['type'] = 'workflow'
                    r['transition_title'] = workflow.getTitleForTransitionOnType(r['action'],
                                                                                 self.context.portal_type)
                    actorid = r['actor']
                    r['actorid'] = actorid
                    if actorid is None:
                        # action performed by an anonymous user
                        anon = _(u'label_anonymous_user',
                                 default=u'Anonymous User')
                        r['actor'] = {'username': anon, 'fullname': anon}
                        r['actor_home'] = ''
                    else:
                        r['actor'] = membership.getMemberInfo(actorid)
                        if r['actor'] is not None:
                            r['actor_home'] = self.navigation_root_url + '/author/' + actorid
                        else:
                            # member info is not available
                            # the user was probably deleted
                            r['actor_home'] = ''
                review_history.reverse()

            except WorkflowException:
                log( 'plone.app.layout.viewlets.content: '
                     '%s has no associated workflow' % self.context.absolute_url(), severity=logging.DEBUG)

        return review_history

    index = ViewPageTemplateFile("review_history.pt")


class ContentHistoryViewlet(WorkflowHistoryViewlet):
    index = ViewPageTemplateFile("content_history.pt")

    @memoize
    def getUserInfo(self, userid):
        mt = getToolByName(self.context, 'portal_membership')
        info=mt.getMemberInfo(userid)
        if info is None:
            return dict(actor_home="",
                        actor=dict(fullname=userid))

        if not info.get("fullname", None):
            info["fullname"]=userid

        return dict(actor=info,
                    actor_home="%s/author/%s" % (self.site_url, userid))

    @memoize
    def revisionHistory(self):
        context = aq_inner(self.context)
        rt = getToolByName(context, "portal_repository")
        allowed = rt.isVersionable(context) and \
            _checkPermission(AccessPreviousVersions, context)
        if not allowed:
            return []
        context_url = context.absolute_url()
        history=rt.getHistoryMetadata(context);
        can_diff = getToolByName(context, "portal_diff", None) is not None

        def morphVersionDataToHistoryFormat(vdata, version_id):
            meta = vdata["metadata"]["sys_metadata"]
            userid = meta["principal"]
            info=dict(type='versioning',
                      action=_(u"edit"),
                      transition_title=_(u"Edit"),
                      actorid=userid,
                      time=meta["timestamp"],
                      comments=meta['comment'],
                      version_id=version_id,
                      review_state=meta["review_state"],
                      preview_url="%s/versions_history_form?version_id=%s#version_preview" %
                                  (context_url, version_id),
                      revert_url="%s/revertversion" % context_url,
                      )
            if can_diff:
                if version_id>0:
                    info["diff_previous_url"]=("%s/@@history?one=%s&two=%s" %
                            (context_url, version_id, version_id-1))
                info["diff_current_url"]=("%s/@@history?one=current&two=%s" %
                            (context_url, version_id))
            info.update(self.getUserInfo(userid))
            return info
        # History may be an empty list
        if not history:
            return history
        version_history = []
        retrieve = history.retrieve
        getId = history.getVersionId
        # Count backwards from most recent to least recent
        for i in xrange(history.getLength(countPurged=False)-1, -1, -1):
            version_history.append(
                morphVersionDataToHistoryFormat(retrieve(i, countPurged=False),
                                                getId(i, countPurged=False)))

        return version_history


    @memoize
    def fullHistory(self):
        history=self.workflowHistory(complete=True) + self.revisionHistory()
        history=[entry for entry in history if entry.get("action", False)]
        history.sort(key=lambda x: x["time"], reverse=True)
        return history


