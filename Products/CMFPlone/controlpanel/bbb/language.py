from zope.component import adapts
from zope.interface import implementer
from zope.component import getUtility
from plone.i18n.interfaces import ILanguageSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.registry.interfaces import IRegistry


@implementer(ILanguageSchema)
class LanguageControlPanelAdapter:

    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ILanguageSchema, prefix="plone")

    def get_default_language(self):
        return self.settings.default_language

    def set_default_language(self, value):
        self.settings.default_language = value

    default_language = property(get_default_language,
                                set_default_language)

    def get_available_languages(self):
        return self.settings.available_languages

    def set_available_languages(self, value):
        self.settings.available_languages = value

    available_languages = property(get_available_languages,
                                   set_available_languages)

    def get_use_combined_language_codes(self):
        return self.settings.use_combined_language_codes

    def set_use_combined_language_codes(self, value):
        self.settings.use_combined_language_codes = value

    use_combined_language_codes = property(get_use_combined_language_codes,
                                           set_use_combined_language_codes)

    def get_display_flags(self):
        return self.settings.display_flags

    def set_display_flags(self, value):
        self.settings.display_flags = value

    display_flags = property(get_display_flags,
                             set_display_flags)

    def get_always_show_selector(self):
        return self.settings.always_show_selector

    def set_always_show_selector(self, value):
        self.settings.always_show_selector = value

    always_show_selector = property(get_always_show_selector,
                                    set_always_show_selector)

    def get_use_content_negotiation(self):
        return self.settings.use_content_negotiation

    def set_use_content_negotiation(self, value):
        self.settings.use_content_negotiation = value

    use_content_negotiation = property(get_use_content_negotiation,
                                       set_use_content_negotiation)

    def get_use_path_negotiation(self):
        return self.settings.use_path_negotiation

    def set_use_path_negotiation(self, value):
        self.settings.use_path_negotiation = value

    use_path_negotiation = property(get_use_path_negotiation,
                                    set_use_path_negotiation)

    def get_use_cookie_negotiation(self):
        return self.settings.use_cookie_negotiation

    def set_use_cookie_negotiation(self, value):
        self.settings.use_cookie_negotiation = value

    use_cookie_negotiation = property(get_use_cookie_negotiation,
                                      set_use_cookie_negotiation)

    def get_authenticated_users_only(self):
        return self.settings.authenticated_users_only

    def set_authenticated_users_only(self, value):
        self.settings.authenticated_users_only = value

    authenticated_users_only = property(get_authenticated_users_only,
                                        set_authenticated_users_only)

    def get_set_cookie_always(self):
        return self.settings.set_cookie_always

    def set_set_cookie_always(self, value):
        self.settings.set_cookie_always = value

    set_cookie_always = property(get_set_cookie_always,
                                 set_set_cookie_always)

    def get_use_subdomain_negotiation(self):
        return self.settings.use_subdomain_negotiation

    def set_use_subdomain_negotiation(self, value):
        self.settings.use_subdomain_negotiation = value

    use_subdomain_negotiation = property(get_use_subdomain_negotiation,
                                         set_use_subdomain_negotiation)

    def get_use_cctld_negotiation(self):
        return self.settings.use_cctld_negotiation

    def set_use_cctld_negotiation(self, value):
        self.settings.use_cctld_negotiation = value

    use_cctld_negotiation = property(get_use_cctld_negotiation,
                                     set_use_cctld_negotiation)

    def get_use_request_negotiation(self):
        return self.settings.use_request_negotiation

    def set_use_request_negotiation(self, value):
        self.settings.use_request_negotiation = value

    use_request_negotiation = property(get_use_request_negotiation,
                                       set_use_request_negotiation)
