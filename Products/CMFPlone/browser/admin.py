from AccessControl import getSecurityManager
from AccessControl.Permissions import view as View
from OFS.interfaces import IApplication
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.GenericSetup import BASE, EXTENSION
from Products.GenericSetup import profile_registry
from Products.GenericSetup.upgrade import normalize_version
from ZPublisher.BaseRequest import DefaultPublishTraverse
from collections import OrderedDict
from operator import itemgetter
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import check as checkCSRF
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component import adapts
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import locales, LoadLocaleError
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IRequest
from zope.schema.interfaces import IVocabularyFactory

import logging
LOGGER = logging.getLogger('Products.CMFPlone')


class AppTraverser(DefaultPublishTraverse):
    adapts(IApplication, IRequest)

    def publishTraverse(self, request, name):
        if name == 'index_html':
            view = queryMultiAdapter(
                (self.context, request), Interface, 'plone-overview')
            if view is not None:
                return view
        return DefaultPublishTraverse.publishTraverse(self, request, name)


class Overview(BrowserView):

    def sites(self, root=None):
        if root is None:
            root = self.context

        result = []
        secman = getSecurityManager()
        for obj in root.values():
            if obj.meta_type is 'Folder':
                result = result + self.sites(obj)
            elif IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(View, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, '_mount_points', {}):
                result.extend(self.sites(root=obj))
        return result

    def outdated(self, obj):
        mig = obj.get('portal_migration', None)
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
            return site.absolute_url() + '/@@plone-upgrade'
        else:
            return self.context.absolute_url() + '/@@plone-root-login'


class RootLoginRedirect(BrowserView):
    """ @@plone-root-login

    This view of the Zope root forces authentication via the root
    acl_users and then redirects elsewhere.
    """

    def __call__(self, came_from=None):
        if came_from is None:
            came_from = self.context.absolute_url()
        self.request.response.redirect(came_from)


class RootLogout(BrowserView):
    """ @@plone-root-logout """

    logout = ViewPageTemplateFile('templates/plone-logged-out.pt')

    def __call__(self):
        response = self.request.response
        realm = response.realm
        response.setStatus(401)
        response.setHeader('WWW-Authenticate', 'basic realm="%s"' % realm, 1)
        response.setBody(self.logout())
        return


class FrontPage(BrowserView):

    index = ViewPageTemplateFile('templates/plone-frontpage.pt')


class AddPloneSite(BrowserView):

    # Profiles that are installed by default,
    # but can be removed later.
    default_extension_profiles = (
        'plone.app.caching:default',
        'plonetheme.barceloneta:default',
    )

    def profiles(self):
        base_profiles = []
        extension_profiles = []

        # profiles available for install/uninstall, but hidden at the time
        # the Plone site is created
        not_installable = [
            'Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow',
        ]
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            not_installable.extend(util.getNonInstallableProfiles())

        for info in profile_registry.listProfileInfo():
            if info.get('type') == EXTENSION and \
               info.get('for') in (IPloneSiteRoot, None):
                profile_id = info.get('id')
                if profile_id not in not_installable:
                    if profile_id in self.default_extension_profiles:
                        info['selected'] = 'selected'
                    extension_profiles.append(info)

        def _key(v):
            # Make sure implicitly selected items come first
            selected = v.get('selected') and 'automatic' or 'manual'
            return '%s-%s' % (selected, v.get('title', ''))
        extension_profiles.sort(key=_key)

        for info in profile_registry.listProfileInfo():
            if info.get('type') == BASE and \
               info.get('for') in (IPloneSiteRoot, None):
                base_profiles.append(info)

        return dict(
            base=tuple(base_profiles),
            default=_DEFAULT_PROFILE,
            extensions=tuple(extension_profiles),
        )

    def browser_language(self):
        language = 'en'
        pl = IUserPreferredLanguages(self.request)
        if pl is not None:
            languages = pl.getPreferredLanguages()
            for httplang in languages:
                parts = (httplang.split('-') + [None, None])[:3]
                if parts[0] == parts[1]:
                    # Avoid creating a country code for simple languages codes
                    parts = [parts[0], None, None]
                try:
                    locale = locales.getLocale(*parts)
                    language = locale.getLocaleID().replace('_', '-').lower()
                    break
                except LoadLocaleError:
                    # Just try the next combination
                    pass
        return language

    def grouped_languages(self, default='en'):
        util = queryUtility(IContentLanguageAvailability)
        available = util.getLanguages(combined=True)
        languages = dict(util.getLanguageListing())

        # Group country specific versions by language
        grouped = OrderedDict()
        for langcode, data in available.items():
            lang = langcode.split('-')[0]
            language = languages.get(lang, lang)  # Label

            struct = grouped.get(lang, {'label': language, 'languages': []})

            langs = struct['languages']
            langs.append({
                'langcode': langcode,
                'label': data.get(u'native', data.get(u'name')),
            })

            grouped[lang] = struct

        # Sort list by language, next by country
        data = sorted(grouped.values(), key=lambda k: k['label'])
        for item in data:
            item['languages'] = sorted(item['languages'], key=lambda k: k['langcode'])
        return data

    def timezones(self):
        tz_vocab = getUtility(
            IVocabularyFactory,
            'plone.app.vocabularies.CommonTimezones'
        )(self.context)

        grouped = OrderedDict()
        tz_values = [it.value for it in tz_vocab]
        for value in tz_values:
            splitted = value.split('/')
            group = splitted.pop(0)
            label = u'/'.join(splitted)

            entries = grouped.get(group, [])
            entries.append({'label': label or group, 'value': value})
            grouped[group] = entries

        return grouped

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            site_id = form.get('site_id', 'Plone')

            # CSRF protect. DO NOT use auto CSRF protection for adding a site
            alsoProvides(self.request, IDisableCSRFProtection)

            # check if keyring is installed on root, disable CSRF protection
            # if it is because it is not installed until a plone site
            # is created
            if queryUtility(IKeyManager) is None:
                LOGGER.info('CSRF protection disabled on initial site '
                            'creation')
            else:
                # we have a keymanager, check csrf protection manually now
                checkCSRF(self.request)
            site = addPloneSite(
                context, site_id,
                title=form.get('title', ''),
                profile_id=form.get('profile_id', _DEFAULT_PROFILE),
                extension_ids=form.get('extension_ids', ()),
                setup_content=form.get('setup_content', False),
                default_language=form.get('default_language', 'en'),
                portal_timezone=form.get('portal_timezone', 'UTC')
            )
            self.request.response.redirect(site.absolute_url())

        return self.index()


class Upgrade(BrowserView):

    def upgrades(self):
        ps = getattr(self.context, 'portal_setup')
        return ps.listUpgrades(_DEFAULT_PROFILE)

    def versions(self):
        pm = getattr(self.context, 'portal_migration')
        result = {}
        result['instance'] = pm.getInstanceVersion()
        result['fs'] = pm.getFileSystemVersion()
        result['equal'] = result['instance'] == result['fs']
        instance_version = normalize_version(result['instance'])
        fs_version = normalize_version(result['fs'])
        result['instance_gt'] = instance_version > fs_version
        result['instance_lt'] = instance_version < fs_version
        result['corelist'] = pm.coreVersions()
        return result

    def __call__(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            # CSRF protect. DO NOT use auto CSRF protection for upgrading sites
            alsoProvides(self.request, IDisableCSRFProtection)

            pm = getattr(self.context, 'portal_migration')
            report = pm.upgrade(
                REQUEST=self.request,
                dry_run=form.get('dry_run', False),
            )
            qi = getattr(self.context, 'portal_quickinstaller')
            pac_installed = qi.isProductInstalled('plone.app.contenttypes')
            pac_installable = qi.isProductInstallable('plone.app.contenttypes')
            advertise_dx_migration = pac_installable and not pac_installed

            return self.index(
                report=report,
                advertise_dx_migration=advertise_dx_migration
            )

        return self.index()
