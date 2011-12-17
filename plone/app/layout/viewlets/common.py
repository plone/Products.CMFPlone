from cgi import escape
from datetime import date
from urllib import unquote

from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from zope.deprecation.deprecation import deprecate
from zope.interface import implements, alsoProvides
from zope.viewlet.interfaces import IViewlet

from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.globals.interfaces import IViewView


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
    @deprecate("Use site_url instead. ViewletBase.portal_url will be removed in Plone 4")
    def portal_url(self):
        return self.site_url


    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.navigation_root_url = self.portal_state.navigation_root_url()

    def render(self):
        # defer to index method, because that's what gets overridden by the template ZCML attribute
        return self.index()

    def index(self):
        raise NotImplementedError(
            '`index` method must be implemented by subclass.')


class TitleViewlet(ViewletBase):
    index = ViewPageTemplateFile('title.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
        page_title = escape(safe_unicode(context_state.object_title()))
        portal_title = escape(safe_unicode(portal_state.navigation_root_title()))
        if page_title == portal_title:
            self.site_title = portal_title
        else:
            self.site_title = u"%s &mdash; %s" % (page_title, portal_title)


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


class SkipLinksViewlet(ViewletBase):
    index = ViewPageTemplateFile('skip_links.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.current_page_url = context_state.current_page_url


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

        props = getToolByName(self.context, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch', False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = "nolivesearchGadget" # don't use "" here!

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class LogoViewlet(ViewletBase):
    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        super(LogoViewlet, self).update()

        portal = self.portal_state.portal()
        bprops = portal.restrictedTraverse('base_properties', None)
        if bprops is not None:
            logoName = bprops.logoName
        else:
            logoName = 'logo.jpg'

        logoTitle = self.portal_state.portal_title()
        self.logo_tag = portal.restrictedTraverse(logoName).tag(title=logoTitle, alt=logoTitle)
        self.navigation_root_title = self.portal_state.navigation_root_title()


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
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]

        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            if path.startswith(action_path + '/'):
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path), action['id']))

        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal' : valid_actions[-1][1]}

        return {'portal' : default_tab}


class PersonalBarViewlet(ViewletBase):

    index = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()
        context = aq_inner(self.context)

        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        sm = getSecurityManager()
        self.user_actions = context_state.actions('user')
        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:
            member = self.portal_state.member()
            userid = member.getId()

            if sm.checkPermission('Portlets: View dashboard', context):
                self.homelink_url = "%s/useractions" % self.navigation_root_url
            else:
                self.homelink_url = "%s/personalize_form" % (
                                        self.navigation_root_url)

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

    @memoize
    def prepareObjectTabs(self, default_tab='view', sort_first=['folderContents']):
        """Prepare the object tabs by determining their order and working
        out which tab is selected. Used in global_contentviews.pt
        """
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

        tabs = []
        found_selected = False
        fallback_action = None

        request_url = self.request['ACTUAL_URL']
        request_url_path = request_url[len(context_url):]

        if request_url_path.startswith('/'):
            request_url_path = request_url_path[1:]

        for action in action_list:
            item = {'title'    : action['title'],
                    'id'       : action['id'],
                    'url'      : '',
                    'selected' : False}

            action_url = action['url'].strip()
            starts = action_url.startswith
            if starts('http') or starts('javascript'):
                item['url'] = action_url
            else:
                item['url'] = '%s/%s' % (context_url, action_url)

            action_method = item['url'].split('/')[-1]

            # Action method may be a method alias:
            # Attempt to resolve to a template.
            action_method = context_fti.queryMethodID(
                action_method, default=action_method
            )
            if action_method:
                request_action = unquote(request_url_path)
                request_action = context_fti.queryMethodID(
                    request_action, default=request_action
                )
                if action_method == request_action:
                    item['selected'] = True
                    found_selected = True

            current_id = item['id']
            if current_id == default_tab:
                fallback_action = item

            tabs.append(item)

        if not found_selected and fallback_action is not None:
            fallback_action['selected'] = True

        def sortOrder(tab):
            try:
                return sort_first.index(tab['id'])
            except ValueError:
                return 255

        tabs.sort(key=sortOrder)
        return tabs


class ManagePortletsFallbackViewlet(ViewletBase):
    """Manage portlets fallback link that sits below content"""

    index = ViewPageTemplateFile('manage_portlets_fallback.pt')

    def update(self):
        ploneview = getMultiAdapter((self.context, self.request), name=u'plone')
        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')

        self.portlet_assignable = context_state.portlet_assignable()
        self.sl = ploneview.have_portlets('plone.leftcolumn', self.context)
        self.sr = ploneview.have_portlets('plone.rightcolumn', self.context)
        self.object_url = context_state.object_url()

    def available(self):
        secman = getSecurityManager()
        if not secman.checkPermission('Portlets: Manage portlets', self.context):
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


class ContentActionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('contentactions.pt')

    def update(self):
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        self.object_actions = context_state.actions('object_actions')

        # The drop-down menus are pulled in via a simple content provider
        # from plone.app.contentmenu. This behaves differently depending on
        # whether the view is marked with IViewView. If our parent view
        # provides that marker, we should do it here as well.
        if IViewView.providedBy(self.__parent__):
            alsoProvides(self, IViewView)

    def icon(self, action):
        return action.get('icon', None)


class FooterViewlet(ViewletBase):
    index = ViewPageTemplateFile('footer.pt')

    def update(self):
        super(FooterViewlet, self).update()
        self.year = date.today().year

