from logging import getLogger
from plone.registry.interfaces import IRegistry
from plone.uuid.handlers import addAttributeUUID
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.events import SiteManagerCreatedEvent
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.Portal import PloneSite
from Products.GenericSetup.tool import SetupTool
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryUtility
from zope.component.hooks import setSite
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectCreatedEvent

_TOOL_ID = 'portal_setup'
_DEFAULT_PROFILE = 'Products.CMFPlone:plone'
_TYPES_PROFILE = 'plone.app.contenttypes:default'
_CONTENT_PROFILE = 'plone.app.contenttypes:plone-content'

# A little hint for PloneTestCase (pre-Plone 6.0)
_IMREALLYPLONE5 = True

# Marker hints for code that needs to know the major Plone version
# Works the same way than zcml condition hints so it contains the current and the
# last ones
PLONE52MARKER = True
PLONE60MARKER = True

logger = getLogger('Plone')


@implementer(INonInstallable)
class NonInstallable:

    def getNonInstallableProducts(self):
        return [
            'CMFDefault', 'Products.CMFDefault',
            'CMFPlone', 'Products.CMFPlone', 'Products.CMFPlone.migrations',
            'CMFTopic', 'Products.CMFTopic',
            'CMFUid', 'Products.CMFUid',
            'DCWorkflow', 'Products.DCWorkflow',
            'PasswordResetTool', 'Products.PasswordResetTool',
            'PlonePAS', 'Products.PlonePAS',
            'PloneLanguageTool', 'Products.PloneLanguageTool',
            'MimetypesRegistry', 'Products.MimetypesRegistry',
            'PortalTransforms', 'Products.PortalTransforms',
            'CMFDiffTool', 'Products.CMFDiffTool',
            'CMFEditions', 'Products.CMFEditions',
            'Products.NuPlone',
            'borg.localrole',
            'plone.app.caching',
            'plone.app.dexterity',
            'plone.app.discussion',
            'plone.app.event',
            'plone.app.intid',
            'plone.app.linkintegrity',
            'plone.app.querystring',
            'plone.app.registry',
            'plone.app.referenceablebehavior',
            'plone.app.relationfield',
            'plone.app.theming',
            'plone.app.users',
            'plone.app.widgets',
            'plone.app.z3cform',
            'plone.formwidget.recurrence',
            'plone.keyring',
            'plone.outputfilters',
            'plone.portlet.static',
            'plone.portlet.collection',
            'plone.protect',
            'plone.resource',
            'plonetheme.barceloneta',
        ]

    def getNonInstallableProfiles(self):
        return [_DEFAULT_PROFILE,
                _CONTENT_PROFILE,
                'Products.CMFDiffTool:CMFDiffTool',
                'Products.CMFEditions:CMFEditions',
                'Products.CMFPlone:dependencies',
                'Products.CMFPlone:testfixture',
                'Products.NuPlone:uninstall',
                'Products.MimetypesRegistry:MimetypesRegistry',
                'Products.PasswordResetTool:PasswordResetTool',
                'Products.PortalTransforms:PortalTransforms',
                'Products.PloneLanguageTool:PloneLanguageTool',
                'Products.PlonePAS:PlonePAS',
                'borg.localrole:default',
                'plone.browserlayer:default',
                'plone.keyring:default',
                'plone.outputfilters:default',
                'plone.portlet.static:default',
                'plone.portlet.collection:default',
                'plone.protect:default',
                'plone.app.contenttypes:default',
                'plone.app.dexterity:default',
                'plone.app.discussion:default',
                'plone.app.event:default',
                'plone.app.linkintegrity:default',
                'plone.app.registry:default',
                'plone.app.relationfield:default',
                'plone.app.theming:default',
                'plone.app.users:default',
                'plone.app.versioningbehavior:default',
                'plone.app.z3cform:default',
                'plone.formwidget.recurrence:default',
                'plone.resource:default',
                ]


def zmi_constructor(context):
    """This is a dummy constructor for the ZMI."""
    url = context.DestinationURL()
    request = context.REQUEST
    return request.response.redirect(url + '/@@plone-addsite?site_id=Plone')


def addPloneSite(context, site_id, title='Plone site', description='',
                 profile_id=_DEFAULT_PROFILE,
                 content_profile_id=_CONTENT_PROFILE, snapshot=False,
                 extension_ids=(), setup_content=True,
                 default_language='en', portal_timezone='UTC'):
    """Add a PloneSite to the context."""

    site = PloneSite(site_id)
    notify(ObjectCreatedEvent(site))
    context[site_id] = site

    site = context[site_id]
    site.setLanguage(default_language)
    # Set the accepted language for the rest of the request.  This makes sure
    # the front-page text gets the correct translation also when your browser
    # prefers non-English and you choose English as language for the Plone
    # Site.
    request = context.REQUEST
    request['HTTP_ACCEPT_LANGUAGE'] = default_language

    site[_TOOL_ID] = SetupTool(_TOOL_ID)
    setup_tool = site[_TOOL_ID]

    notify(SiteManagerCreatedEvent(site))
    setSite(site)

    setup_tool.setBaselineContext('profile-%s' % profile_id)
    setup_tool.runAllImportStepsFromProfile('profile-%s' % profile_id)

    reg = queryUtility(IRegistry, context=site)
    reg['plone.portal_timezone'] = portal_timezone
    reg['plone.available_timezones'] = [portal_timezone]
    reg['plone.default_language'] = default_language
    reg['plone.available_languages'] = [default_language]

    # Install default content types profile if user do not select "example content"
    # during site creation.
    content_types_profile = content_profile_id if setup_content else _TYPES_PROFILE

    setup_tool.runAllImportStepsFromProfile(f'profile-{content_types_profile}')

    props = dict(
        title=title,
        description=description,
    )
    # Do this before applying extension profiles, so the settings from a
    # properties.xml file are applied and not overwritten by this
    site.manage_changeProperties(**props)

    for extension_id in extension_ids:
        try:
            setup_tool.runAllImportStepsFromProfile(
                'profile-%s' % extension_id)
        except Exception as msg:
            IStatusMessage(request).add(_(
                'Could not install ${profile_id}: ${error_msg}! '
                'Please try to install it manually using the "Addons" '
                'controlpanel and report any issues to the '
                'addon maintainers.',
                mapping={
                    'profile_id': extension_id,
                    'error_msg': msg.args,
                }),
                type='error')
            logger.exception(
                'Error while installing addon {}. '
                'See traceback below for details.'.format(extension_id))

    if snapshot is True:
        setup_tool.createSnapshot('initial_configuration')

    return site
