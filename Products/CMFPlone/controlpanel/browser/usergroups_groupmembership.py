from Products.CMFPlone import PloneMessageFactory as _
from zExceptions import Forbidden
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups import \
    UsersGroupsControlPanelView
from Products.CMFPlone.utils import normalizeString


class GroupMembershipControlPanel(UsersGroupsControlPanelView):

    def update(self):
        self.groupname = getattr(self.request, 'groupname')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.group = self.gtool.getGroupById(self.groupname)
        if self.group is None:
            return

        self.grouptitle = self.group.getGroupTitleOrName() or self.groupname

        self.request.set('grouproles', self.group.getRoles()
                         if self.group else [])
        self.canAddUsers = True
        if 'Manager' in self.request.get('grouproles') and not self.is_zope_manager:
            self.canAddUsers = False

        self.groupquery = self.makeQuery(groupname=self.groupname)
        self.groupkeyquery = self.makeQuery(key=self.groupname)

        form = self.request.form
        submitted = form.get('form.submitted', False)

        self.searchResults = []
        self.searchString = ''
        self.newSearch = False

        if submitted:
            # add/delete before we search so we don't show stale results
            toAdd = form.get('add', [])
            if toAdd:
                if not self.canAddUsers:
                    raise Forbidden

                for u in toAdd:
                    self.gtool.addPrincipalToGroup(
                        u, self.groupname, self.request)
                self.context.plone_utils.addPortalMessage(_('Changes made.'))

            toDelete = form.get('delete', [])
            if toDelete:
                for u in toDelete:
                    self.gtool.removePrincipalFromGroup(
                        u, self.groupname, self.request)
                self.context.plone_utils.addPortalMessage(_('Changes made.'))

            search = form.get('form.button.Search', None) is not None
            edit = form.get('form.button.Edit', None) is not None and toDelete
            add = form.get('form.button.Add', None) is not None and toAdd
            findAll = form.get('form.button.FindAll', None) is not None and \
                not self.many_users
            # The search string should be cleared when one of the
            # non-search buttons has been clicked.
            if findAll or edit or add:
                form['searchstring'] = ''
            self.searchString = form.get('searchstring', '')
            if findAll or bool(self.searchString):
                self.searchResults = self.getPotentialMembers(
                    self.searchString)

            if search or findAll:
                self.newSearch = True

        self.groupMembers = self.getMembers()

    def __call__(self):
        self.update()
        return self.index()

    def isGroup(self, itemName):
        return self.gtool.isGroup(itemName)

    def getMembers(self):
        searchResults = self.gtool.getGroupMembers(self.groupname)

        groupResults = []
        userResults = []
        for principal_id in searchResults:
            principal = self.gtool.getGroupById(principal_id)
            if principal is not None:
                groupResults.append(principal)
                continue
            principal = self.mtool.getMemberById(principal_id)
            if principal is not None:
                userResults.append(principal)

        groupResults.sort(key=lambda x: normalizeString(x.getGroupTitleOrName()))
        userResults.sort(key=lambda x: normalizeString(x.getProperty('fullname') or ''))

        return groupResults + userResults

    def getPotentialMembers(self, searchString):
        ignoredUsersGroups = [
            x.id for x in self.getMembers() + [self.group, ] if x is not None]
        return self.membershipSearch(searchString, ignore=ignoredUsersGroups)
