from Products.CMFPlone import PloneMessageFactory as _
from zExceptions import Forbidden
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups import \
    UsersGroupsControlPanelView
from Products.CMFPlone.utils import normalizeString


class UserMembershipControlPanel(UsersGroupsControlPanelView):

    def update(self):
        self.userid = getattr(self.request, 'userid')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.member = self.mtool.getMemberById(self.userid)

        form = self.request.form

        self.searchResults = []
        self.searchString = ''
        self.newSearch = False

        if form.get('form.submitted', False):
            delete = form.get('delete', [])
            if delete:
                for groupname in delete:
                    self.gtool.removePrincipalFromGroup(
                        self.userid, groupname, self.request)
                self.context.plone_utils.addPortalMessage(_('Changes made.'))

            add = form.get('add', [])
            if add:
                for groupname in add:
                    group = self.gtool.getGroupById(groupname)
                    if 'Manager' in group.getRoles() and not self.is_zope_manager:
                        raise Forbidden

                    self.gtool.addPrincipalToGroup(
                        self.userid, groupname, self.request)
                self.context.plone_utils.addPortalMessage(_('Changes made.'))

        search = form.get('form.button.Search', None) is not None
        findAll = form.get('form.button.FindAll',
                           None) is not None and not self.many_groups
        self.searchString = not findAll and form.get('searchstring', '') or ''

        if findAll or not self.many_groups or self.searchString != '':
            self.searchResults = self.getPotentialGroups(self.searchString)

        if search or findAll:
            self.newSearch = True

        self.groups = self.getGroups()

    def __call__(self):
        self.update()
        return self.index()

    def getGroups(self):
        groupResults = [self.gtool.getGroupById(
            m) for m in self.gtool.getGroupsForPrincipal(self.member)]
        groupResults.sort(key=lambda x: x is not None and normalizeString(
            x.getGroupTitleOrName()))
        return [i for i in groupResults if i]

    def getPotentialGroups(self, searchString):
        ignoredGroups = [x.id for x in self.getGroups() if x is not None]
        return self.membershipSearch(searchString, searchUsers=False, ignore=ignoredGroups)
