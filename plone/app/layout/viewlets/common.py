from zope.interface import implements
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


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

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal_url = self.portal_state.portal_url()

    def render(self):
        raise NotImplementedError(
            '`render` method must be implemented by subclass.')


class TitleViewlet(ViewletBase):

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title

    def render(self):
        return u"<title>%s &mdash; %s</title>" % (
            safe_unicode(self.page_title()),
            safe_unicode(self.portal_title()))


class TableOfContentsViewlet(ViewletBase):
    render = ViewPageTemplateFile('toc.pt')

    def update(self):
        obj = aq_base(self.context)
        getTableContents = getattr(obj, 'getTableContents', None)
        self.enabled = False
        if getTableContents is not None:
            self.enabled = getTableContents()


class SkipLinksViewlet(ViewletBase):
    render = ViewPageTemplateFile('skip_links.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.current_page_url = context_state.current_page_url


class SiteActionsViewlet(ViewletBase):
    render = ViewPageTemplateFile('site_actions.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_actions = context_state.actions().get('site_actions', None)


class SearchBoxViewlet(ViewletBase):
    render = ViewPageTemplateFile('searchbox.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        self.portal_url = portal_state.portal_url()

        props = getToolByName(aq_inner(self.context), 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch', False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = ""

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class LogoViewlet(ViewletBase):
    render = ViewPageTemplateFile('logo.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

        self.navigation_root_url = portal_state.navigation_root_url()

        portal = portal_state.portal()
        logoName = portal.restrictedTraverse('base_properties').logoName
        self.logo_tag = portal.restrictedTraverse(logoName).tag()

        self.portal_title = portal_state.portal_title()


class GlobalSectionsViewlet(ViewletBase):
    render = ViewPageTemplateFile('sections.pt')

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
    render = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

        self.portal_url = portal_state.portal_url()

        self.user_actions = context_state.actions().get('user', None)

        plone_utils = getToolByName(aq_inner(self.context), 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.anonymous = portal_state.anonymous()

        member = portal_state.member()
        member_info = tools.membership().getMemberInfo(member.getId())
        fullname = member_info.get('fullname', '')
        if fullname:
            self.user_name = fullname
        else:
            self.user_name = member.getUserName()


class PathBarViewlet(ViewletBase):
    render = ViewPageTemplateFile('path_bar.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

        self.navigation_root_url = portal_state.navigation_root_url()

        self.is_rtl = portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
