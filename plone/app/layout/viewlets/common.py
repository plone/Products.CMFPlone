from cgi import escape
from datetime import date
from urllib import unquote

from plone.registry.interfaces import IRegistry

from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.deprecation.deprecation import deprecate
from zope.i18n import translate
from zope.interface import implements, alsoProvides
from zope.viewlet.interfaces import IViewlet

from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.utils import safe_unicode, getSiteLogo
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.protect.utils import addTokenToUrl


class ViewletBase(BrowserView):
    """ Base class with common functions for link viewlets.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager=None):
        super(ViewletBase, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    @property
    @deprecate("Use site_url instead. " +
               "ViewletBase.portal_url will be removed in Plone 4")
    def portal_url(self):
        return self.site_url

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.navigation_root_url = self.portal_state.navigation_root_url()

    def render(self):
        # defer to index method, because that's what gets overridden by the
        # template ZCML attribute
        return self.index()

    def index(self):
        raise NotImplementedError(
            '`index` method must be implemented by subclass.')


class TitleViewlet(ViewletBase):
    index = ViewPageTemplateFile('title.pt')

    @property
    @memoize
    def site_title_setting(self):
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema,
                                              prefix="plone",
                                              check=False)
        return site_settings.site_title

    @property
    @memoize
    def page_title(self):
        '''
        Get the page title. If we are in the portal_factory we want use the
        "Add $FTI_TITLE" form (see #12117).

        NOTE: other implementative options can be:
         - to use "Untitled" instead of "Add" or
         - to check the isTemporary method of the edit view instead of the
           creation_flag
        '''
        if (hasattr(aq_base(self.context), 'isTemporary') and
                self.context.isTemporary()):
            # if we are in the portal_factory we want the page title to be
            # "Add fti title"
            portal_types = getToolByName(self.context, 'portal_types')
            fti = portal_types.getTypeInfo(self.context)
            return translate('heading_add_item',
                             domain='plone',
                             mapping={'itemtype': fti.Title()},
                             context=self.request,
                             default='Add ${itemtype}')

        # If we are on portal root, look up the portal title from registry
        if IPloneSiteRoot.providedBy(self.context):
            return self.site_title_setting

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return escape(safe_unicode(context_state.object_title()))

    def update(self):
        if IPloneSiteRoot.providedBy(self.context):
            self.site_title = self.site_title_setting
            return
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal_title = escape(safe_unicode(portal_state
                                           .navigation_root_title()))
        if self.page_title == portal_title:
            self.site_title = portal_title
        else:
            self.site_title = u"%s &mdash; %s" % (self.page_title,
                                                  portal_title)


class DublinCoreViewlet(ViewletBase):
    index = ViewPageTemplateFile('dublin_core.pt')

    def update(self):
        plone_utils = getToolByName(self.context, 'plone_utils')
        context = aq_inner(self.context)
        self.metatags = plone_utils.listMetaTags(context).items()


class TableOfContentsViewlet(ViewletBase):
    index = ViewPageTemplateFile('toc.pt')

    def update(self):
        obj = aq_base(self.context)
        getTableContents = getattr(obj, 'getTableContents', None)
        self.enabled = False
        if getTableContents is not None:
            try:
                self.enabled = getTableContents()
            except KeyError:
                # schema not updated yet
                self.enabled = False
        # handle dexterity-behavior
        toc = getattr(obj, 'table_of_contents', None)
        if toc is not None:
            self.enabled = toc


class SiteActionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('site_actions.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_actions = context_state.actions('site_actions')


class SearchBoxViewlet(ViewletBase):
    index = ViewPageTemplateFile('searchbox.pt')

    def update(self):
        super(SearchBoxViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix='plone')
        self.livesearch = search_settings.enable_livesearch

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class LogoViewlet(ViewletBase):
    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        super(LogoViewlet, self).update()

        # TODO: should this be changed to settings.site_title?
        self.navigation_root_title = self.portal_state.navigation_root_title()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema,
                                         prefix="plone",
                                         check=False)
        self.logo_title = settings.site_title
        self.img_src = getSiteLogo()


class GlobalSectionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('sections.pt')

    def update(self):
        context = aq_inner(self.context)
        portal_tabs_view = getMultiAdapter((context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs()

        self.selected_tabs = self.selectedTabs(portal_tabs=self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']

    def selectedTabs(self, default_tab='index_html', portal_tabs=()):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        plone_url = getNavigationRootObject(self.context, portal).absolute_url()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]
        path_list = path.split('/')
        if len(path_list) <= 1:
            return {'portal': default_tab}

        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            action_path_list = action_path.split('/')
            if action_path_list[1] == path_list[1]:
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path_list), action['id']))

        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal': valid_actions[-1][1]}

        return {'portal': default_tab}


class PersonalBarViewlet(ViewletBase):

    def update(self):
        super(PersonalBarViewlet, self).update()
        context = aq_inner(self.context)

        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        user_actions = context_state.actions('user')
        self.user_actions = []
        for action in user_actions:
            info = {
                'title': action['title'],
                'href': action['url'],
                'id': 'personaltools-{}'.format(action['id']),
                'target': 'link_target' in action and action['link_target'] or None,
                }
            modal = action.get('modal')
            if modal:
                info['class'] = 'pat-plone-modal'
                info['data-pat-plone-modal'] = modal
            self.user_actions.append(info)

        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:
            member = self.portal_state.member()
            userid = member.getId()

            self.homelink_url = "%s/useractions" % self.navigation_root_url

            membership = getToolByName(context, 'portal_membership')
            member_info = membership.getMemberInfo(userid)
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid


class ContentViewsViewlet(ViewletBase):
    index = ViewPageTemplateFile('contentviews.pt')
    menu_template = ViewPageTemplateFile('menu.pt')

    default_tab = 'nothing'
    primary = ['folderContents', 'edit', 'view']

    def update(self):
        # The drop-down menus are pulled in via a simple content provider
        # from plone.app.contentmenu. This behaves differently depending on
        # whether the view is marked with IViewView. If our parent view
        # provides that marker, we should do it here as well.
        super(ContentViewsViewlet, self).update()
        if IViewView.providedBy(self.__parent__):
            alsoProvides(self, IViewView)

        self.tabSet1, self.tabSet2 = self.getTabSets()

    @memoize
    def getTabSets(self):
        context = aq_inner(self.context)
        context_url = context.absolute_url()
        context_fti = context.getTypeInfo()

        context_state = getMultiAdapter(
            (context, self.request), name=u'plone_context_state'
        )
        actions = context_state.actions

        action_list = []
        if context_state.is_structural_folder():
            action_list = actions('folder')
        action_list.extend(actions('object'))
        action_list.extend(actions('object_actions'))

        tabSet1 = []
        tabSet2 = []
        found_selected = False
        fallback_action = None

        try:
            request_url = self.request['ACTUAL_URL']
        except KeyError:
            # not a real request, could be a test. Let's not fail.
            request_url = context_url
        request_url_path = request_url[len(context_url):]

        if request_url_path.startswith('/'):
            request_url_path = request_url_path[1:]

        for item in action_list:
            item.update({'selected': False})

            action_url = item['url'].strip()
            starts = action_url.startswith
            if starts('http') or starts('javascript'):
                item['url'] = action_url
            else:
                item['url'] = '%s/%s' % (context_url, action_url)
            item['url'] = addTokenToUrl(item['url'], self.request)

            action_method = item['url'].split('/')[-1].split('?')[0]

            # Action method may be a method alias:
            # Attempt to resolve to a template.
            action_method = context_fti.queryMethodID(
                action_method, default=action_method
            )
            if action_method:
                request_action = unquote(request_url_path).split('?')[0]
                request_action = context_fti.queryMethodID(
                    request_action, default=request_action
                )
                if action_method == request_action and item['id'] != 'view':
                    item['selected'] = True
                    found_selected = True

            current_id = item['id']
            if current_id == self.default_tab:
                fallback_action = item

            modal = item.get('modal', None)
            item['cssClass'] = ''
            if modal:
                item['cssClass'] += ' pat-plone-modal'
                if 'ajax_load' not in item['url']:
                    item['url'] += '?ajax_load=1'

            if item['id'] in self.primary:
                tabSet1.append(item)
            else:
                tabSet2.append(item)

        if not found_selected and fallback_action is not None:
            fallback_action['selected'] = True

        tabSet1.sort(key=lambda item: self.primary.index(item['id']))
        return tabSet1, tabSet2

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
            lockable = getattr(context.aq_explicit,
                               'wl_isLocked', None
                               ) is not None
            locked = lockable and context.wl_isLocked()

        if not locked:
            return ""

        portal = self.portal_state.portal()
        icon = portal.restrictedTraverse('lock_icon.png')
        return icon.tag(title='Locked')


class ManagePortletsFallbackViewlet(ViewletBase):
    """Manage portlets fallback link that sits below content"""

    index = ViewPageTemplateFile('manage_portlets_fallback.pt')

    def update(self):
        ploneview = getMultiAdapter((
            self.context, self.request), name=u'plone')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        self.portlet_assignable = context_state.portlet_assignable()
        self.sl = ploneview.have_portlets('plone.leftcolumn', self.context)
        self.sr = ploneview.have_portlets('plone.rightcolumn', self.context)
        self.object_url = context_state.object_url()

    def available(self):
        secman = getSecurityManager()
        has_manage_portlets_permission = secman.checkPermission(
            'Portlets: Manage portlets',
            self.context
        )
        if not has_manage_portlets_permission:
            return False
        elif not self.sl and not self.sr and self.portlet_assignable:
            return True


class PathBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('path_bar.pt')

    def update(self):
        super(PathBarViewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()


class TinyLogoViewlet(ViewletBase):
    index = ViewPageTemplateFile('tiny_logo.pt')


class FooterViewlet(ViewletBase):
    index = ViewPageTemplateFile('footer.pt')

    def update(self):
        super(FooterViewlet, self).update()
        self.year = date.today().year

    def render_footer_portlets(self):
        """
        You might ask, why is this necessary. Well, let me tell you a story...

        plone.app.portlets, in order to provide @@manage-portlets on a context,
        overrides the IPortletRenderer for the IManageContextualPortletsView view.
        See plone.portlets and plone.app.portlets

        Seems fine right? Well, most of the time it is. Except, here. Previously,
        we were just using the syntax like `provider:plone.footerportlets` to
        render the footer portlets. Since this tal expression was inside
        a viewlet, the view is no longer IManageContextualPortletsView when
        visiting @@manage-portlets. Instead, it was IViewlet.
        See zope.contentprovider

        In to fix this short coming, we render the portlet column by
        manually doing the multi adapter lookup and then manually
        doing the rendering for the content provider.
        See zope.contentprovider
        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name='plone.footerportlets')
        portlet_manager.update()
        return portlet_manager.render()
