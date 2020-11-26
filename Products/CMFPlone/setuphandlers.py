from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.interfaces import IMigrationTool
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager \
    import AcceleratedHTTPCacheManager
from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from borg.localrole.utils import replace_local_role_manager
from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.i18n.locales import LoadLocaleError
from zope.i18n.locales import locales


def addCacheHandlers(portal):
    """ Add RAM and AcceleratedHTTP cache handlers """
    mgrs = [(AcceleratedHTTPCacheManager, 'HTTPCache'),
            (RAMCacheManager, 'RAMCache'),
            (RAMCacheManager, 'ResourceRegistryCache'),
            ]
    for mgr_class, mgr_id in mgrs:
        existing = portal.get(mgr_id, None)
        if existing is None:
            portal[mgr_id] = mgr_class(mgr_id)
        else:
            unwrapped = aq_base(existing)
            if not isinstance(unwrapped, mgr_class):
                del portal[mgr_id]
                portal[mgr_id] = mgr_class(mgr_id)


def purgeProfileVersions(portal):
    """
    Purge profile dependency versions.
    """
    setup = getToolByName(portal, 'portal_setup')
    setup._profile_upgrade_versions = {}


def setProfileVersion(portal):
    """
    Set profile version.
    """
    mt = queryUtility(IMigrationTool)
    mt.setInstanceVersion(mt.getFileSystemVersion())
    setup = getToolByName(portal, 'portal_setup')
    version = setup.getVersionForProfile(_DEFAULT_PROFILE)
    setup.setLastVersionForProfile(_DEFAULT_PROFILE, version)


def assignTitles(portal):
    titles = {
        'acl_users': 'User / Group storage and authentication settings',
        'caching_policy_manager': 'Settings related to proxy caching',
        'content_type_registry': 'MIME type settings',
        'error_log': 'Error and exceptions log viewer',
        'MailHost': 'Mail server settings for outgoing mail',
        'mimetypes_registry': 'MIME types recognized by Plone',
        'plone_utils': 'Various utility methods',
        'portal_actions': 'Contains custom tabs and buttons',
        'portal_calendar': 'Controls how events are shown',
        'portal_catalog': 'Indexes all content in the site',
        'portal_controlpanel': 'Registry of control panel screen',
        'portal_diff': 'Settings for content version comparisions',
        'portal_groupdata': 'Handles properties on groups',
        'portal_groups': 'Handles group related functionality',
        'portal_languages': 'Language specific settings',
        'portal_membership': 'Handles membership policies',
        'portal_memberdata': 'Handles the available properties on members',
        'portal_migration': 'Upgrades to newer Plone versions',
        'portal_password_reset': 'Handles password retention policy',
        'portal_properties': 'General settings registry',
        'portal_registration': 'Handles registration of new users',
        'portal_setup': 'Add-on and configuration management',
        'portal_skins': 'Controls skin behaviour (search order etc)',
        'portal_transforms': 'Handles data conversion between MIME types',
        'portal_types': 'Controls the available content types in your portal',
        'portal_url': 'Methods to anchor you to the root of your Plone site',
        'portal_view_customizations': 'Template customizations',
        'portal_workflow': 'Contains workflow definitions for your portal',
        'reference_catalog': 'Catalog of content references',
        'translation_service': 'Provides access to the translation machinery',
    }
    for oid, obj in portal.items():
        title = titles.get(oid, None)
        if title:
            setattr(aq_base(obj), 'title', title)


def dummy_import_step(context):
    """Dummy import step.

    The plone-final import step used to call importFinalSteps below.
    But plone-final was never guaranteed to be run as final step.  So
    more and more import steps were added to its dependencies to let it
    run later and later.  Not nice.

    With Products.GenericSetup 1.8.2, we can add a post_handler to a
    profile (and a pre_handler).  We now do that.  So the plone-final
    import step is no longer needed.  But others may depend on it, so we
    keep it for now.  This dummy import step handler is meant for
    that.
    """
    pass


def importFinalSteps(context):
    """Final Plone import steps.

    This was an import step, but is now registered as post_handler
    specifically for our main 'plone' (profiles/default) profile.
    """
    site = getSite()

    # Unset all profile upgrade versions in portal_setup.  Our default
    # profile should only be applied when creating a new site, so this
    # list of versions should be empty.  But some tests apply it too.
    # This should not be done as it should not be needed.  The profile
    # is a base profile, which means all import steps are run in purge
    # mode.  So for example an extra workflow added by
    # plone.app.discussion is purged.  When plone.app.discussion is
    # still in the list of profile upgrade versions, with the default
    # dependency strategy it will not be reapplied again, which leaves
    # you with a site that misses stuff.  So: when applying our
    # default profile, start with a clean slate in these versions.
    purgeProfileVersions(site)

    # Set out default profile version.
    setProfileVersion(site)

    # Install our dependencies
    st = getToolByName(site, "portal_setup")
    st.runAllImportStepsFromProfile(
        "profile-Products.CMFPlone:dependencies")

    assignTitles(site)
    replace_local_role_manager(site)
    addCacheHandlers(site)

    first_weekday_setup(context)
    timezone_setup(context)

    set_zsqlmethods_permissions(site)

    # setup resource overrides plone.resource
    persistentDirectory = getUtility(IResourceDirectory, name="persistent")
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistentDirectory:
        persistentDirectory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)


def set_zsqlmethods_permissions(site):
    """The permission to use Products.ZSQLMethods only makes sense when
    ZSQLMethods is installed. In Zope 4 that is sometimes not the case.

    The following xml was taken from rolemap.xml:
    <permission name="Use Database Methods" acquire="True">
      <role name="Site Administrator"/>
    </permission>
    """
    try:
        import Products.ZSQLMethods  # noqa
    except ImportError:
        return
    site.manage_permission(
        'Use Database Methods',
        ['Site Administrator'],
        False)


def updateWorkflowRoleMappings(context):
    """
    If an extension profile (such as the testfixture one) switches default,
    workflows, this import handler will make sure object security works
    properly.
    """
    # Only run step if a flag file is present
    if context.readDataFile('plone-update-workflow-rolemap.txt') is None:
        return
    site = context.getSite()
    portal_workflow = getToolByName(site, 'portal_workflow')
    portal_workflow.updateRoleMappings()


def first_weekday_setup(context):
    """Set the first day of the week based on the portal's locale.
    """
    reg = getUtility(IRegistry)
    if reg.get('plone.first_weekday') is not None:
        # don't overwrite if it's already set
        return

    first = 6
    try:
        site = getSite()
        # find the locale implied by the portal's language
        language = site.Language()
        parts = (language.split('-') + [None, None])[:3]
        locale = locales.getLocale(*parts)
        # look up first day of week
        gregorian_calendar = locale.dates.calendars.get('gregorian', None)
        if gregorian_calendar is not None:
            day = gregorian_calendar.week.get('firstDay', 7)
            first = 6 if day == 0 else day - 1
    except LoadLocaleError:
        # If we cannot get the locale, just Sunday as first weekday
        pass

    # save setting
    reg['plone.first_weekday'] = first


def timezone_setup(context):
    """Set the timezone from server locale
    """
    timezone = 'UTC'
    # TODO: get a /sane/ locale from the server to use.
    # this is not high priority
    # see plone.event.utils
    reg = getUtility(IRegistry)
    if not reg["plone.portal_timezone"]:
        reg['plone.portal_timezone'] = timezone
    if not reg['plone.available_timezones']:
        reg['plone.available_timezones'] = [timezone]
