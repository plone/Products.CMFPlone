from Acquisition import aq_inner
from Products.CMFPlone.controlpanel.browser.usergroups import \
    UsersGroupsControlPanelView
from plone.protect import CheckAuthenticator
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


class GroupDetailsControlPanel(UsersGroupsControlPanelView):

    def __call__(self):
        context = aq_inner(self.context)

        self.gtool = getToolByName(context, 'portal_groups')
        self.gdtool = getToolByName(context, 'portal_groupdata')
        self.regtool = getToolByName(context, 'portal_registration')
        self.groupname = getattr(self.request, 'groupname', None)
        self.grouproles = self.request.set('grouproles', [])
        self.group = self.gtool.getGroupById(self.groupname)
        self.grouptitle = self.groupname
        if self.group is not None:
            self.grouptitle = self.group.getGroupTitleOrName()

        self.request.set('grouproles', self.group.getRoles() if self.group else [])

        submitted = self.request.form.get('form.submitted', False)
        if submitted:
            CheckAuthenticator(self.request)

            msg = _(u'No changes made.')
            self.group = None

            title = self.request.form.get('title', None)
            description = self.request.form.get('description', None)
            addname = self.request.form.get('addname', None)

            if addname:
                if not self.regtool.isMemberIdAllowed(addname):
                    msg = _(u'The group name you entered is not valid.')
                    IStatusMessage(self.request).add(msg, 'error')
                    return self.index()

                success = self.gtool.addGroup(addname, (), (), title=title,
                                              description=description,
                                              REQUEST=self.request)
                if not success:
                    msg = _(u'Could not add group ${name}, perhaps a user or group with '
                            u'this name already exists.', mapping={u'name' : addname})
                    IStatusMessage(self.request).add(msg, 'error')
                    return self.index()

                self.group = self.gtool.getGroupById(addname)
                msg = _(u'Group ${name} has been added.',
                        mapping={u'name' : addname})

            elif self.groupname:
                self.gtool.editGroup(self.groupname, roles=None, groups=None,
                                     title=title, description=description,
                                     REQUEST=context.REQUEST)
                self.group = self.gtool.getGroupById(self.groupname)
                msg = _(u'Changes saved.')

            else:
                msg = _(u'Group name required.')

            processed = {}
            for id, property in self.gdtool.propertyItems():
                processed[id] = self.request.get(id, None)

            if self.group:
                # for what reason ever, the very first group created does not exist
                self.group.setGroupProperties(processed)

            IStatusMessage(self.request).add(msg, type=self.group and 'info' or 'error')
            if self.group and not self.groupname:
                target_url = '%s/%s' % (self.context.absolute_url(), '@@usergroup-groupprefs')
                self.request.response.redirect(target_url)
                return ''

        return self.index()
