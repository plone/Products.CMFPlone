import logging

from plone.memoize.instance import memoize
from zope.component import getMultiAdapter, queryMultiAdapter

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import log

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets import ViewletBase


class DocumentActionsViewlet(ViewletBase):

    index = ViewPageTemplateFile("document_actions.pt")

    def update(self):
        super(DocumentActionsViewlet, self).update()

        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.actions = self.context_state.actions('document_actions')


class DocumentBylineViewlet(ViewletBase):

    index = ViewPageTemplateFile("document_byline.pt")

    def update(self):
        super(DocumentBylineViewlet, self).update()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.anonymous = self.portal_state.anonymous()

    def show(self):
        properties = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        allowAnonymousViewAbout = site_properties.getProperty(
            'allowAnonymousViewAbout', True)
        return not self.anonymous or allowAnonymousViewAbout

    def show_history(self):
        if not _checkPermission('CMFEditions: Access previous versions', self.context):
            return False
        if IViewView.providedBy(self.__parent__):
            return True
        return False

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

    def creator(self):
        return self.context.Creator()

    def author(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(self.creator())

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

    def isExpired(self):
        if base_hasattr(self.context, 'expires'):
            return self.context.expires().isPast()
        return False

    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')


class ContentRelatedItems(ViewletBase):

    index = ViewPageTemplateFile("document_relateditems.pt")

    def related_items(self):
        context = aq_inner(self.context)
        res = ()
        if base_hasattr(context, 'getRawRelatedItems'):
            catalog = getToolByName(context, 'portal_catalog')
            related = context.getRawRelatedItems()
            if not related:
                return ()
            brains = catalog(UID=related)
            if brains:
                # build a position dict by iterating over the items once
                positions = dict([(v, i) for (i, v) in enumerate(related)])
                # We need to keep the ordering intact
                res = list(brains)
                def _key(brain):
                    return positions.get(brain.UID, -1)
                res.sort(key=_key)
        return res


class WorkflowHistoryViewlet(ViewletBase):

    index = ViewPageTemplateFile("review_history.pt")

    def workflowHistory(self, complete=True):
        """Return workflow history of this context.

        Taken from plone_scripts/getWorkflowHistory.py
        """
        context = aq_inner(self.context)
        # check if the current user has the proper permissions
        if not (_checkPermission('Request review', context) or
            _checkPermission('Review portal content', context)):
            return []

        workflow = getToolByName(context, 'portal_workflow')
        membership = getToolByName(context, 'portal_membership')

        review_history = []

        try:
            # get total history
            review_history = workflow.getInfoFor(context, 'review_history')

            if not complete:
                # filter out automatic transitions.
                review_history = [r for r in review_history if r['action']]
            else:
                review_history = list(review_history)

            portal_type = context.portal_type
            anon = _(u'label_anonymous_user', default=u'Anonymous User')

            for r in review_history:
                r['type'] = 'workflow'
                r['transition_title'] = workflow.getTitleForTransitionOnType(
                    r['action'], portal_type) or _("Create")
                r['state_title'] = workflow.getTitleForStateOnType(
                    r['review_state'], portal_type)
                actorid = r['actor']
                r['actorid'] = actorid
                if actorid is None:
                    # action performed by an anonymous user
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
            log('plone.app.layout.viewlets.content: '
                '%s has no associated workflow' % context.absolute_url(),
                severity=logging.DEBUG)

        return review_history


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

    def revisionHistory(self):
        context = aq_inner(self.context)
        if not _checkPermission(AccessPreviousVersions, context):
            return []

        rt = getToolByName(context, "portal_repository", None)
        if rt is None or not rt.isVersionable(context):
            return []

        context_url = context.absolute_url()
        history=rt.getHistoryMetadata(context);
        portal_diff = getToolByName(context, "portal_diff", None)
        can_diff = portal_diff is not None \
            and len(portal_diff.getDiffForPortalType(context.portal_type)) > 0

        def morphVersionDataToHistoryFormat(vdata, version_id):
            meta = vdata["metadata"]["sys_metadata"]
            userid = meta["principal"]
            info=dict(type='versioning',
                      action=_(u"Edited"),
                      transition_title=_(u"Edited"),
                      actorid=userid,
                      time=meta["timestamp"],
                      comments=meta['comment'],
                      version_id=version_id,
                      preview_url="%s/versions_history_form?version_id=%s#version_preview" %
                                  (context_url, version_id),
                      revert_url="%s/revertversion" % context_url,
                      )
            if can_diff:
                if version_id>0:
                    info["diff_previous_url"]=("%s/@@history?one=%s&two=%s" %
                            (context_url, version_id, version_id-1))
                if not rt.isUpToDate(context, version_id):
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

    def fullHistory(self):
        history = self.workflowHistory() + self.revisionHistory()
        if len(history) == 0:
            return None
        history.sort(key=lambda x: x["time"], reverse=True)
        return history

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                        domain='plonelocales')


class ContentHistoryView(ContentHistoryViewlet):

    index = ViewPageTemplateFile("content_history.pt")

    def __init__(self, context, request):
        super(ContentHistoryView, self).__init__(context, request, None, None)
        self.update()
