import logging

from plone.memoize.instance import memoize
from zope.component import getMultiAdapter, queryMultiAdapter

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from plone.protect.authenticator import createToken
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import log
from zope.component import getUtility

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets import ViewletBase
from plone.app.content.browser.interfaces import IFolderContentsView

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.relationfield')
except pkg_resources.DistributionNotFound:
    HAS_RELATIONFIELD = False
else:
    from plone.app.relationfield.behavior import IRelatedItems
    HAS_RELATIONFIELD = True

try:
    pkg_resources.get_distribution('plone.app.multilingual')
except pkg_resources.DistributionNotFound:
    HAS_PAM = False
else:
    HAS_PAM = True
    from plone.app.multilingual.interfaces import ITranslatable
    from plone.app.multilingual.interfaces import ITranslationManager
    from plone.app.multilingual.browser.vocabularies import translated_languages


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
        self.has_pam = HAS_PAM

    def show(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone',
        )
        return not self.anonymous or settings.allow_anon_views_about

    def show_history(self):
        has_access_preview_versions_permission = _checkPermission(
            'CMFEditions: Access previous versions',
            self.context
        )
        if not has_access_preview_versions_permission:
            return False
        if IViewView.providedBy(self.__parent__):
            return True
        if IFolderContentsView.providedBy(self.__parent__):
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
            lockable = getattr(
                context.aq_explicit, 'wl_isLocked', None) is not None
            locked = lockable and context.wl_isLocked()

        if not locked:
            return ""

        portal = self.portal_state.portal()
        icon = portal.restrictedTraverse('lock_icon.png')
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

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')

    def pub_date(self):
        """Return object effective date.

        Return None if publication date is switched off in global site settings
        or if Effective Date is not set on object.
        """
        # check if we are allowed to display publication date
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema,
            prefix='plone')

        if not settings.display_publication_date_in_byline:
            return None

        # check if we have Effective Date set
        date = self.context.EffectiveDate()
        if not date or date == 'None':
            return None

        return DateTime(date)

    def get_translations(self):
        cts = []
        if ITranslatable.providedBy(self.context):
            t_langs = translated_languages(self.context)
            context_translations = ITranslationManager(self.context).get_translations()
            for lang in t_langs:
                cts.append(dict(lang_native=lang.title,
                                url=context_translations[lang.value].absolute_url()))

        return cts


class HistoryByLineView(BrowserView):
    """ DocumentByLine information for content history view """

    index = ViewPageTemplateFile('history_view.pt')

    def update(self):
        context = self.context
        self.portal_state = getMultiAdapter((context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.anonymous = self.portal_state.anonymous()
        self.has_pam = HAS_PAM

    def __call__(self):
        self.update()

        return self.index()

    def show(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone',
        )
        return not self.anonymous or settings.allow_anon_views_about

    def show_history(self):
        has_access_preview_versions_permission = _checkPermission(
            'CMFEditions: Access previous versions',
            self.context
        )
        if not has_access_preview_versions_permission:
            return False
        if IViewView.providedBy(self.__parent__):
            return True
        if IFolderContentsView.providedBy(self.__parent__):
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
            lockable = getattr(
                context.aq_explicit, 'wl_isLocked', None) is not None
            locked = lockable and context.wl_isLocked()

        if not locked:
            return ""

        portal = self.portal_state.portal()
        icon = portal.restrictedTraverse('lock_icon.png')
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

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')

    def pub_date(self):
        """Return object effective date.

        Return None if publication date is switched off in global site settings
        or if Effective Date is not set on object.
        """
        # check if we are allowed to display publication date
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema,
            prefix='plone')

        if not settings.display_publication_date_in_byline:
            return None

        # check if we have Effective Date set
        date = self.context.EffectiveDate()
        if not date or date == 'None':
            return None

        return DateTime(date)

    def get_translations(self):
        cts = []
        if ITranslatable.providedBy(self.context):
            t_langs = translated_languages(self.context)
            context_translations = ITranslationManager(self.context).get_translations()
            for lang in t_langs:
                cts.append(dict(lang_native=lang.title,
                                url=context_translations[lang.value].absolute_url()))

        return cts


class ContentRelatedItems(ViewletBase):

    index = ViewPageTemplateFile("document_relateditems.pt")

    def related_items(self):
        context = aq_inner(self.context)
        res = ()

        # Archetypes
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

        # Dexterity
        if HAS_RELATIONFIELD and IRelatedItems.providedBy(context):
            related = context.relatedItems
            if not related:
                return ()
            res = self.related2brains(related)

        return res

    def related2brains(self, related):
        """Return a list of brains based on a list of relations. Will filter
        relations if the user has no permission to access the content.

        :param related: related items
        :type related: list of relations
        :return: list of catalog brains
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = []
        for r in related:
            path = r.to_path
            # the query will return an empty list if the user
            # has no permission to see the target object
            brains.extend(catalog(path=dict(query=path, depth=0)))
        return brains


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
                        r['actor_home'] = self.navigation_root_url + \
                            '/author/' + actorid
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
        info = mt.getMemberInfo(userid)
        if info is None:
            return dict(actor_home="",
                        actor=dict(fullname=userid))

        if not info.get("fullname", None):
            info["fullname"] = userid

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
        history = rt.getHistoryMetadata(context)
        portal_diff = getToolByName(context, "portal_diff", None)
        can_diff = portal_diff is not None \
            and len(portal_diff.getDiffForPortalType(context.portal_type)) > 0
        can_revert = _checkPermission('CMFEditions: Revert to previous versions', context)

        def morphVersionDataToHistoryFormat(vdata, version_id):
            meta = vdata["metadata"]["sys_metadata"]
            userid = meta["principal"]
            token = createToken()
            preview_url = \
                "%s/versions_history_form?version_id=%s&_authenticator=%s#version_preview" % (  # noqa
                    context_url,
                    version_id,
                    token
                )
            info = dict(
                type='versioning',
                action=_(u"Edited"),
                transition_title=_(u"Edited"),
                actorid=userid,
                time=meta["timestamp"],
                comments=meta['comment'],
                version_id=version_id,
                preview_url=preview_url,
            )
            if can_diff:
                if version_id > 0:
                    info["diff_previous_url"] = (
                        "%s/@@history?one=%s&two=%s&_authenticator=%s" %
                        (context_url, version_id, version_id - 1, token)
                    )
                if not rt.isUpToDate(context, version_id):
                    info["diff_current_url"] = (
                        "%s/@@history?one=current&two=%s&_authenticator=%s" %
                        (context_url, version_id, token)
                    )
            if can_revert:
                info["revert_url"] = "%s/revertversion" % context_url
            else:
                info["revert_url"] = None
            info.update(self.getUserInfo(userid))
            return info

        # History may be an empty list
        if not history:
            return history

        version_history = []
        retrieve = history.retrieve
        getId = history.getVersionId
        # Count backwards from most recent to least recent
        for i in xrange(history.getLength(countPurged=False) - 1, -1, -1):
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
        # util = getToolByName(self.context, 'translation_service')
        return DateTime(time).ISO()
        # return util.ulocalized_time(time, long_format, time_only, self.context,
        #                             domain='plonelocales')


class ContentHistoryView(ContentHistoryViewlet):

    def __init__(self, context, request):
        super(ContentHistoryView, self).__init__(context, request, None, None)
        self.update()

    def __call__(self):
        return self.index()
