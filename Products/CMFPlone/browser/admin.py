from AccessControl import getSecurityManager
from AccessControl.Permissions import view as View
from collections import OrderedDict
from OFS.interfaces import IApplication
from plone.base.interfaces import INonInstallable
from plone.base.interfaces import IPloneSiteRoot
from plone.base.utils import get_installer
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import check as checkCSRF
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.GenericSetup import BASE
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.GenericSetup.upgrade import normalize_version
from urllib import parse
from ZODB.broken import Broken
from zope.component import adapter
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import LoadLocaleError
from zope.i18n.locales import locales
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IRequest
from zope.schema.interfaces import IVocabularyFactory
from ZPublisher.BaseRequest import DefaultPublishTraverse

import logging
import pkg_resources


try:
    pkg_resources.get_distribution("plone.volto")
    HAS_VOLTO = True
except pkg_resources.DistributionNotFound:
    HAS_VOLTO = False
LOGGER = logging.getLogger("Products.CMFPlone")


@adapter(IApplication, IRequest)
class AppTraverser(DefaultPublishTraverse):
    def publishTraverse(self, request, name):
        if name == "index_html":
            view = queryMultiAdapter(
                (self.context, request), Interface, "plone-overview"
            )
            if view is not None:
                return view
        return DefaultPublishTraverse.publishTraverse(self, request, name)


class Overview(BrowserView):
    has_volto = HAS_VOLTO

    def sites(self, root=None):
        if root is None:
            root = self.context

        result = []
        secman = getSecurityManager()
        candidates = (obj for obj in root.values() if not isinstance(obj, Broken))
        for obj in candidates:
            if obj.meta_type == "Folder":
                result = result + self.sites(obj)
            elif IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(View, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, "_mount_points", {}):
                result.extend(self.sites(root=obj))
        return result

    def outdated(self, obj):
        # Try to pick the portal_migration as an attribute
        # (Plone 5 unmigrated site root) or as an item
        mig = getattr(obj, "portal_migration", None) or obj.get(
            "portal_migration", None
        )
        if mig is not None:
            return mig.needUpgrading()
        return False

    def can_manage(self):
        secman = getSecurityManager()
        return secman.checkPermission(ManagePortal, self.context)

    def upgrade_url(self, site, can_manage=None):
        if can_manage is None:
            can_manage = self.can_manage()
        if can_manage:
            return site.absolute_url() + "/@@plone-upgrade"
        else:
            return self.context.absolute_url() + "/@@plone-root-login"


class RootLoginRedirect(BrowserView):
    """@@plone-root-login

    This view of the Zope root forces authentication via the root
    acl_users and then redirects elsewhere.
    """

    def __call__(self, came_from=None):
        if came_from is not None:
            # see if this is a relative url or an absolute
            if len(parse.urlparse(came_from)[1]) == 0:
                # No host specified, so url is relative.  Get an absolute url.
                # Note: '\\domain.org' is not recognised as host,
                # which is good.
                came_from = parse.urljoin(
                    self.context.absolute_url() + "/",
                    came_from,
                )
            elif not came_from.startswith(self.context.absolute_url()):
                # Note: we cannot use portal_url.isURLInPortal here, because we
                # are not in a Plone portal, but in the Zope root.
                came_from = None
        if came_from is None:
            came_from = self.context.absolute_url()
        self.request.response.redirect(came_from)


class RootLogout(BrowserView):
    """@@plone-root-logout"""

    logout = ViewPageTemplateFile("templates/plone-admin-logged-out.pt")

    def __call__(self):
        response = self.request.response
        realm = response.realm
        response.setStatus(401)
        response.setHeader("WWW-Authenticate", 'basic realm="%s"' % realm, 1)
        response.setBody(self.logout())
        return


class FrontPage(BrowserView):
    index = ViewPageTemplateFile("templates/plone-frontpage.pt")


class AddPloneSite(BrowserView):
    # Profiles that are installed by default,
    # but can be removed later.
    default_extension_profiles = (
        "plone.app.caching:default",
        "plonetheme.barceloneta:default",
    )
    # Let's have a separate list for Volto.
    volto_default_extension_profiles = (
        "plone.app.caching:default",
        "plonetheme.barceloneta:default",
        "plone.volto:default",
    )

    def profiles(self):
        base_profiles = []
        extension_profiles = []
        if HAS_VOLTO and not self.request.get("classic"):
            selected_extension_profiles = self.volto_default_extension_profiles
        else:
            selected_extension_profiles = self.default_extension_profiles

        # profiles available for install/uninstall, but hidden at the time
        # the Plone site is created
        not_installable = [
            "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
        ]
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            not_installable.extend(
                util.getNonInstallableProfiles()
                if hasattr(util, "getNonInstallableProfiles")
                else []
            )

        for info in profile_registry.listProfileInfo():
            if info.get("type") == EXTENSION and info.get("for") in (
                IPloneSiteRoot,
                None,
            ):
                profile_id = info.get("id")
                if profile_id not in not_installable:
                    if profile_id in selected_extension_profiles:
                        info["selected"] = "selected"
                    extension_profiles.append(info)

        def _key(v):
            # Make sure implicitly selected items come first
            selected = v.get("selected") and "automatic" or "manual"
            return "{}-{}".format(selected, v.get("title", ""))

        extension_profiles.sort(key=_key)

        for info in profile_registry.listProfileInfo():
            if info.get("type") == BASE and info.get("for") in (IPloneSiteRoot, None):
                base_profiles.append(info)

        return dict(
            base=tuple(base_profiles),
            default=_DEFAULT_PROFILE,
            extensions=tuple(extension_profiles),
        )

    def browser_language(self):
        language = "en"
        pl = IUserPreferredLanguages(self.request)
        if pl is not None:
            languages = pl.getPreferredLanguages()
            for httplang in languages:
                parts = (httplang.split("-") + [None, None])[:3]
                if parts[0] == parts[1]:
                    # Avoid creating a country code for simple languages codes
                    parts = [parts[0], None, None]
                try:
                    locale = locales.getLocale(*parts)
                    language = locale.getLocaleID().replace("_", "-").lower()
                    break
                except LoadLocaleError:
                    # Just try the next combination
                    pass
        return language

    def grouped_languages(self, default="en"):
        util = queryUtility(IContentLanguageAvailability)
        available = util.getLanguages(combined=True)
        languages = dict(util.getLanguageListing())

        # Group country specific versions by language
        grouped = OrderedDict()
        for langcode, data in available.items():
            lang = langcode.split("-")[0]
            language = languages.get(lang, lang)  # Label

            struct = grouped.get(lang, {"label": language, "languages": []})

            langs = struct["languages"]
            langs.append(
                {
                    "langcode": langcode,
                    "label": data.get("native", data.get("name")),
                }
            )

            grouped[lang] = struct

        # Sort list by language, next by country
        data = sorted(grouped.values(), key=lambda k: k["label"])
        for item in data:
            item["languages"] = sorted(
                item["languages"], key=lambda k: k["label"].lower()
            )
        return data

    def timezones(self):
        tz_vocab = getUtility(
            IVocabularyFactory, "plone.app.vocabularies.CommonTimezones"
        )(self.context)

        grouped = OrderedDict()
        tz_values = [it.value for it in tz_vocab]
        for value in tz_values:
            split = value.split("/")
            group = split.pop(0)
            label = "/".join(split)

            entries = grouped.get(group, [])
            entries.append({"label": label or group, "value": value})
            grouped[group] = entries

        return grouped

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get("form.submitted", False)
        if submitted:
            site_id = form.get("site_id", "Plone")

            # CSRF protect. DO NOT use auto CSRF protection for adding a site
            alsoProvides(self.request, IDisableCSRFProtection)

            # check if keyring is installed on root, disable CSRF protection
            # if it is because it is not installed until a plone site
            # is created
            if queryUtility(IKeyManager) is None:
                LOGGER.info("CSRF protection disabled on initial site " "creation")
            else:
                # we have a keymanager, check csrf protection manually now
                checkCSRF(self.request)

            site = addPloneSite(
                context,
                site_id,
                title=form.get("title", ""),
                profile_id=form.get("profile_id", _DEFAULT_PROFILE),
                extension_ids=form.get("extension_ids", ()),
                setup_content=form.get("setup_content", False),
                default_language=form.get("default_language", "en"),
                portal_timezone=form.get("portal_timezone", "UTC"),
            )
            self.request.response.redirect(site.absolute_url())
            return ""

        return self.index()


class Upgrade(BrowserView):
    def upgrades(self):
        pm = getattr(self.context, "portal_migration")
        return pm.listUpgrades()

    def versions(self):
        pm = getattr(self.context, "portal_migration")
        result = {}
        result["instance"] = pm.getInstanceVersion()
        result["fs"] = pm.getFileSystemVersion()
        result["equal"] = result["instance"] == result["fs"]
        instance_version = normalize_version(result["instance"])
        fs_version = normalize_version(result["fs"])
        result["instance_gt"] = instance_version > fs_version
        result["instance_lt"] = instance_version < fs_version
        result["corelist"] = pm.coreVersions()
        return result

    def __call__(self):
        form = self.request.form
        submitted = form.get("form.submitted", False)
        if submitted:
            # CSRF protect. DO NOT use auto CSRF protection for upgrading sites
            alsoProvides(self.request, IDisableCSRFProtection)

            pm = getattr(self.context, "portal_migration")
            report = pm.upgrade(
                REQUEST=self.request,
                dry_run=form.get("dry_run", False),
            )
            return self.index(
                report=report,
            )

        return self.index()

    def can_migrate_to_volto(self):
        if not HAS_VOLTO:
            return False
        pm = getattr(self.context, "portal_migration")
        if pm.getInstanceVersion() < "6005":
            return False
        try:
            from plone.volto.browser import migrate_to_volto  # noqa: F401
        except ImportError:
            return False
        installer = get_installer(self.context, self.request)
        return not installer.is_product_installed("plone.volto")
