from logging import getLogger
from plone.base.interfaces import INonInstallable
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.events import SiteManagerCreatedEvent
from Products.CMFPlone.Portal import PloneSite
from Products.GenericSetup.tool import SetupTool
from zope.component import queryUtility
from zope.component.hooks import setSite
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectCreatedEvent

import warnings


_TOOL_ID = "portal_setup"
_DEFAULT_PROFILE = "Products.CMFPlone:plone"
_TYPES_PROFILE = "plone.app.contenttypes:default"
_CONTENT_PROFILE = "plone.app.contenttypes:plone-content"

# A little hint for PloneTestCase (pre-Plone 6.0)
_IMREALLYPLONE5 = True

# Marker hints for code that needs to know the major Plone version
# Works the same way as zcml condition hints so it contains the current and the
# previous ones
PLONE52MARKER = True
PLONE60MARKER = True
PLONE61MARKER = True

logger = getLogger("Plone")


@implementer(INonInstallable)
class NonInstallable:
    def getNonInstallableProducts(self):
        return [
            "CMFDefault",
            "Products.CMFDefault",
            "CMFPlone",
            "Products.CMFPlone",
            "Products.CMFPlone.migrations",
            "CMFTopic",
            "Products.CMFTopic",
            "CMFUid",
            "Products.CMFUid",
            "DCWorkflow",
            "Products.DCWorkflow",
            "PasswordResetTool",
            "Products.PasswordResetTool",
            "PlonePAS",
            "Products.PlonePAS",
            "PloneLanguageTool",
            "Products.PloneLanguageTool",
            "MimetypesRegistry",
            "Products.MimetypesRegistry",
            "PortalTransforms",
            "Products.PortalTransforms",
            "CMFDiffTool",
            "Products.CMFDiffTool",
            "CMFEditions",
            "Products.CMFEditions",
            "Products.NuPlone",
            "borg.localrole",
            "plone.app.dexterity",
            "plone.app.event",
            "plone.app.intid",
            "plone.app.linkintegrity",
            "plone.app.querystring",
            "plone.app.registry",
            "plone.app.referenceablebehavior",
            "plone.app.relationfield",
            "plone.app.theming",
            "plone.app.users",
            "plone.app.z3cform",
            "plone.formwidget.recurrence",
            "plone.keyring",
            "plone.outputfilters",
            "plone.portlet.static",
            "plone.portlet.collection",
            "plone.protect",
            "plone.resource",
            "plonetheme.barceloneta",
        ]

    def getNonInstallableProfiles(self):
        return [
            _DEFAULT_PROFILE,
            _CONTENT_PROFILE,
            "Products.CMFDiffTool:CMFDiffTool",
            "Products.CMFEditions:CMFEditions",
            "Products.CMFPlone:dependencies",
            "Products.CMFPlone:testfixture",
            "Products.NuPlone:uninstall",
            "Products.MimetypesRegistry:MimetypesRegistry",
            "Products.PasswordResetTool:PasswordResetTool",
            "Products.PortalTransforms:PortalTransforms",
            "Products.PloneLanguageTool:PloneLanguageTool",
            "Products.PlonePAS:PlonePAS",
            "borg.localrole:default",
            "plone.browserlayer:default",
            "plone.keyring:default",
            "plone.outputfilters:default",
            "plone.portlet.static:default",
            "plone.portlet.collection:default",
            "plone.protect:default",
            "plone.app.contenttypes:default",
            "plone.app.dexterity:default",
            "plone.app.event:default",
            "plone.app.linkintegrity:default",
            "plone.app.registry:default",
            "plone.app.relationfield:default",
            "plone.app.theming:default",
            "plone.app.users:default",
            "plone.app.versioningbehavior:default",
            "plone.app.z3cform:default",
            "plone.formwidget.recurrence:default",
            "plone.resource:default",
        ]


def zmi_constructor(context):
    """This is a dummy constructor for the ZMI."""
    url = context.DestinationURL()
    request = context.REQUEST
    return request.response.redirect(url + "/@@plone-addsite?site_id=Plone")


def addPloneSite(
    context,
    site_id,
    title="Plone site",
    description="",
    profile_id=_DEFAULT_PROFILE,
    snapshot=False,
    content_profile_id=None,
    extension_ids=(),
    setup_content=None,
    default_language="en",
    portal_timezone="UTC",
    distribution_name=None,
    **kwargs,
):
    """Add a PloneSite to the context."""
    if distribution_name:
        from plone.distribution.api import site as site_api

        # Pass all arguments and keyword arguments in the answers,
        # But the 'distribution_name' is not needed there.
        answers = {
            "site_id": site_id,
            "title": title,
            "description": description,
            "profile_id": profile_id,
            "snapshot": snapshot,
            "content_profile_id": content_profile_id,
            "extension_ids": extension_ids,
            "setup_content": setup_content,
            "default_language": default_language,
            "portal_timezone": portal_timezone,
        }
        answers.update(kwargs)
        site = site_api._create_site(
            context=context, distribution_name=distribution_name, answers=answers
        )
        setSite(site)
        return site

    if content_profile_id is not None:
        warnings.warn(
            "addPloneSite ignores the content_profile_id keyword argument "
            "since Plone 6.1. In Plone 7 it will be removed.",
            DeprecationWarning,
        )
    if setup_content is not None:
        warnings.warn(
            "addPloneSite ignores the setup_content keyword argument "
            "since Plone 6.1, treating it as always False. "
            "In Plone 7 it will be removed.",
            DeprecationWarning,
        )

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
    request["HTTP_ACCEPT_LANGUAGE"] = default_language

    site[_TOOL_ID] = SetupTool(_TOOL_ID)
    setup_tool = site[_TOOL_ID]

    notify(SiteManagerCreatedEvent(site))
    setSite(site)

    try:
        setup_tool.setBaselineContext("profile-%s" % profile_id)
        setup_tool.runAllImportStepsFromProfile("profile-%s" % profile_id)

        reg = queryUtility(IRegistry, context=site)
        reg["plone.portal_timezone"] = portal_timezone
        reg["plone.available_timezones"] = [portal_timezone]
        reg["plone.default_language"] = default_language
        reg["plone.available_languages"] = [default_language]
        reg["plone.site_title"] = title

        props = dict(
            title=title,
            description=description,
        )
        # Do this before applying extension profiles, so the settings from a
        # properties.xml file are applied and not overwritten by this
        site.manage_changeProperties(**props)

        for extension_id in extension_ids:
            try:
                setup_tool.runAllImportStepsFromProfile(f"profile-{extension_id}")
            except Exception:
                logger.error(f"Error while installing profile {extension_id}:")
                raise

        if snapshot is True:
            setup_tool.createSnapshot("initial_configuration")

        return site
    except Exception:
        setSite(None)
        raise
