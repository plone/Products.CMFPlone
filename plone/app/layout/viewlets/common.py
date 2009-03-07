from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet
from zope.deprecation.deprecation import deprecate

from plone.app.layout.globals.interfaces import IViewView 

from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from cgi import escape
from urllib import quote_plus


class ViewletBase(BrowserView):
    """ Base class with common functions for link viewlets.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
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

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title

    def index(self):
        portal_title = safe_unicode(self.portal_title())
        page_title = safe_unicode(self.page_title())
        if page_title == portal_title:
            return u"<title>%s</title>" % (escape(portal_title))
        else:
            return u"<title>%s &mdash; %s</title>" % (
                escape(safe_unicode(page_title)),
                escape(safe_unicode(portal_title)))


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
        self.site_actions = context_state.actions().get('site_actions', None)


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
            self.search_input_id = ""

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class LogoViewlet(ViewletBase):
    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        super(LogoViewlet, self).update()

        portal = self.portal_state.portal()
        logoName = portal.restrictedTraverse('base_properties').logoName
        self.logo_tag = portal.restrictedTraverse(logoName).tag()

        self.portal_title = self.portal_state.portal_title()


class GlobalSectionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('sections.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions()
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)

        selectedTabs = self.context.restrictedTraverse('selectedTabs')
        self.selected_tabs = selectedTabs('index_html',
                                          self.context,
                                          self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']


class PersonalBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        
        sm = getSecurityManager()

        self.user_actions = context_state.actions().get('user', None)

        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:
        
            member = self.portal_state.member()
            userid = member.getId()
            
            if sm.checkPermission('Portlets: Manage own portlets', self.context):
                self.homelink_url = self.navigation_root_url + '/dashboard'
            else:
                if userid.startswith('http:') or userid.startswith('https:'):
                    self.homelink_url = self.site_url + '/author/?author=' + userid
                else:
                    self.homelink_url = self.site_url + '/author/' + quote_plus(userid)
            
            member_info = tools.membership().getMemberInfo(member.getId())
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

        self.object_actions = context_state.actions().get('object_actions', [])

        plone_utils = getToolByName(context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.portal_actionicons = getToolByName(context, 'portal_actionicons')
        
        # The drop-down menus are pulled in via a simple content provider
        # from plone.app.contentmenu. This behaves differently depending on
        # whether the view is marked with IViewView. If our parent view 
        # provides that marker, we should do it here as well.
        if IViewView.providedBy(self.__parent__):
            alsoProvides(self, IViewView)
        
    def icon(self, action):
        icon = action.get('icon', None)
        if icon is None:
            icon = self.getIconFor('content_actions', action['id'])
        return icon
