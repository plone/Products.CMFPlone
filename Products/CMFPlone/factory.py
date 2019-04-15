# -*- coding: utf-8 -*-
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.events import SiteManagerCreatedEvent
from Products.CMFPlone.interfaces import INonInstallable
from Products.GenericSetup.tool import SetupTool
from Products.statusmessages.interfaces import IStatusMessage
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.event import notify
from zope.interface import implementer
from zope.site.hooks import setSite

_TOOL_ID = 'portal_setup'
_DEFAULT_PROFILE = 'Products.CMFPlone:plone'
_CONTENT_PROFILE = 'plone.app.contenttypes:plone-content'

# A little hint for PloneTestCase
_IMREALLYPLONE5 = True


@implementer(INonInstallable)
class NonInstallable(object):

    def getNonInstallableProducts(self):
        return [
            'Archetypes', 'Products.Archetypes',
            'CMFDefault', 'Products.CMFDefault',
            'CMFPlone', 'Products.CMFPlone', 'Products.CMFPlone.migrations',
            'CMFTopic', 'Products.CMFTopic',
            'CMFUid', 'Products.CMFUid',
            'DCWorkflow', 'Products.DCWorkflow',
            'PasswordResetTool', 'Products.PasswordResetTool',
            'PlonePAS', 'Products.PlonePAS',
            'wicked.at',
            'PloneLanguageTool', 'Products.PloneLanguageTool',
            'CMFFormController', 'Products.CMFFormController',
            'MimetypesRegistry', 'Products.MimetypesRegistry',
            'PortalTransforms', 'Products.PortalTransforms',
            'CMFDiffTool', 'Products.CMFDiffTool',
            'CMFEditions', 'Products.CMFEditions',
            'Products.NuPlone',
            'borg.localrole',
            'plone.app.blob',
            'plone.app.caching',
            'plone.app.collection',
            'plone.app.dexterity',
            'plone.app.discussion',
            'plone.app.event',
            'plone.app.imaging',
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
                u'Products.Archetypes:Archetypes',
                u'Products.ATContentTypes:default',
                u'Products.CMFDiffTool:CMFDiffTool',
                u'Products.CMFEditions:CMFEditions',
                u'Products.CMFFormController:CMFFormController',
                u'Products.CMFPlone:dependencies',
                u'Products.CMFPlone:testfixture',
                u'Products.CMFQuickInstallerTool:CMFQuickInstallerTool',
                u'Products.NuPlone:uninstall',
                u'Products.MimetypesRegistry:MimetypesRegistry',
                u'Products.PasswordResetTool:PasswordResetTool',
                u'Products.PortalTransforms:PortalTransforms',
                u'Products.PloneLanguageTool:PloneLanguageTool',
                u'Products.PlonePAS:PlonePAS',
                u'borg.localrole:default',
                u'plone.browserlayer:default',
                u'plone.keyring:default',
                u'plone.outputfilters:default',
                u'plone.portlet.static:default',
                u'plone.portlet.collection:default',
                u'plone.protect:default',
                u'plone.app.blob:default',
                u'plone.app.blob:file-replacement',
                u'plone.app.blob:image-replacement',
                u'plone.app.blob:sample-type',
                u'plone.app.collection:default',
                u'plone.app.contenttypes:default',
                u'plone.app.dexterity:default',
                u'plone.app.discussion:default',
                u'plone.app.event:default',
                u'plone.app.imaging:default',
                u'plone.app.linkintegrity:default',
                u'plone.app.registry:default',
                u'plone.app.relationfield:default',
                u'plone.app.theming:default',
                u'plone.app.users:default',
                u'plone.app.versioningbehavior:default',
                u'plone.app.z3cform:default',
                u'plone.formwidget.recurrence:default',
                u'plone.resource:default',
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
    context._setObject(site_id, PloneSite(site_id))
    site = context._getOb(site_id)
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

    if setup_content:
        setup_tool.runAllImportStepsFromProfile(
            'profile-%s' % content_profile_id)

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
            IStatusMessage(request).add(
                'Could not install {}: {}\n'
                'Please try to install it manually using the "Addons" '
                'controlpanel and report any issues to the '
                'addon maintainers'.format(extension_id, msg.args),
                type='warning')

    if snapshot is True:
        setup_tool.createSnapshot('initial_configuration')

    return site
