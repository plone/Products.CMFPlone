"""
CMFPlone setup handlers.
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone import migrations as migs
from Products.CMFPlone.Portal import member_indexhtml

class PloneGenerator:

    def installProducts(self, p):
        """QuickInstaller install of required Products"""
        # XXX These should all be done via a CMFSetup handler
        qi = getToolByName(p, 'portal_quickinstaller')
        qi.installProduct('Archetypes', locked=0)
        qi.installProduct('CMFFormController', locked=1)
        qi.installProduct('GroupUserFolder', locked=1)
        qi.installProduct('PasswordResetTool', locked=1)
        qi.installProduct('PlonePAS', locked=1)
        qi.installProduct('CMFPlacefulWorkflow', locked=0)
        qi.installProduct('kupu', locked=0)
        #qi.notifyInstalled('ResourceRegistries', locked=0)
        #qi.notifyInstalled('ATContentTypes', locked=0)
        #qi.notifyInstalled('ATReferenceBrowserWidget', locked=0)
        qi.notifyInstalled('CMFCalendar', locked=1)
        qi.notifyInstalled('CMFActionIcons', locked=1)

    def customizePortalOptions(self, p):
        p.manage_permission( cmfpermissions.ListFolderContents, \
                             ('Manager', 'Member', 'Owner',), acquire=1 )
        stool = getToolByName(p, 'portal_skins')
        stool.allow_any=0 # Skin changing for users is turned off by default

        syntool = getToolByName(p, 'portal_syndication')
        syntool.editProperties(isAllowed=1)
        #p.icon = 'misc_/CMFPlone/plone_icon'

    # XXX: This should all be done by custom setuphandlers, possibly
    # using Kapil's XMLIO
    def setupPortalContent(self, p):
        """
        Import default plone content
        """

        # News topic
        _createObjectByType('Topic', p, id='news', title='News', description='Site News')
        topic = p.news
        type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue('News Item')
        sort_crit = topic.addCriterion('created','ATSortCriterion')
        state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
        state_crit.setValue('published')
        topic.setSortCriterion('effective', True)
        topic.setLayout('folder_summary_view')

        # Events topic
        _createObjectByType('Topic', p, id='events', title='Events', description='Site Events')
        topic = p.events
        type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue('Event')
        sort_crit = topic.addCriterion('start','ATSortCriterion')
        state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
        state_crit.setValue('published')
        date_crit = topic.addCriterion('start', 'ATFriendlyDateCriteria')
        # Set date reference to now
        date_crit.setValue(0)
        # Only take events in the future
        date_crit.setDateRange('+') # This is irrelevant when the date is now
        date_crit.setOperation('more')

        # Previous events subtopic
        _createObjectByType('Topic', topic, id='previous', title='Past Events',
                            description="Events which have already happened.")
        topic = topic.previous
        topic.setAcquireCriteria(True)
        sort_crit = topic.addCriterion('start','ATSortCriterion')
        sort_crit.setReversed(True)
        date_crit = topic.addCriterion('start','ATFriendlyDateCriteria')
        # Set date reference to now
        date_crit.setValue(0)
        # Only take events in the past
        date_crit.setDateRange('-') # This is irrelevant when the date is now
        date_crit.setOperation('less')

        # configure Members folder (already added by the content import)
        members = getattr(p , 'Members')
        members.setTitle('Members')
        members.setDescription("Container for portal members' home directories")
        members.manage_addProperty('right_slots', [], 'lines')
        # XXX: Not sure why reindex is needed, but it doesn't seem to happen otherwise
        members.reindexObject()

        # add index_html to Members area
        addPy = members.manage_addProduct['PythonScripts'].manage_addPythonScript
        addPy('index_html')
        index_html = getattr(members, 'index_html')
        index_html.write(member_indexhtml)
        index_html.ZPythonScript_setTitle('Member Search')

    def setupGroups(self, p):
        """
        Create Plone's default set of groups.
        """
        gtool = getToolByName(p, 'portal_groups')
        gtool.addGroup('Administrators', roles=['Manager'])
        gtool.addGroup('Reviewers', roles=['Reviewer'])

    def performMigrationActions(self, p):
        """
        Perform any necessary migration steps.
        """
        out = []
        migs.v2_1.alphas.addDefaultTypesToPortalFactory(p, out)
        migs.v2_1.rcs.enableSyndicationOnTopics(p, out)

    def setATCTToolVersion(self, p):
        """
        Have to specify the portal_atct version number by hand since
        we no longer call it's installer.

        XXX This should really be handled w/ a specific import handler
        for the tool.
        """
        atcttool = getToolByName(p, 'portal_atct')
        atcttool.setVersionFromFS()
        
def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    site = context.getSite()

    gen = PloneGenerator()

    gen.installProducts(site)
    gen.customizePortalOptions(site)


def importFinalSteps(context):
    """
    Final plone import steps.
    """
    site = context.getSite()

    gen = PloneGenerator()
    gen.setupPortalContent(site)
    gen.setupGroups(site)
    gen.performMigrationActions(site)
    gen.setATCTToolVersion(site)
