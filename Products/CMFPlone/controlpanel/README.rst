Plone Controlpanel
==================

All control panel related settings are stored in plone.app.registry and
can be looked up like follow.

First we lookup the registry utility::

  >>> from zope.component import getUtility
  >>> from plone.registry.interfaces import IRegistry
  >>> registry = getUtility(IRegistry)

Now we use the schema 'ISearchSchema' to lookup for a RecordProxy object with
all fields::

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> search_settings = registry.forInterface(ISearchSchema, prefix='plone')

Now we an get and set all fields of the schema above like::

  >>> search_settings.enable_livesearch
  True

If you want to change a setting, just change the attribute::

  >>> search_settings.enable_livesearch = False

Now the enable_livesearch should disabled::

  >>> search_settings.enable_livesearch
  False

For more informations about how to access and manipulate Plone registry entries, have a look at the `plone.registry documentation <https://github.com/plone/plone.registry/blob/master/plone/registry/registry.rst>`_:


Editing Control Panel
---------------------

  >>> from Products.CMFPlone.interfaces import IEditingSchema
  >>> editing_settings = registry.forInterface(IEditingSchema, prefix='plone')

  >>> editing_settings.visible_ids
  False

  >>> editing_settings.default_editor
  u'TinyMCE'

  >>> editing_settings.ext_editor
  False

  >>> editing_settings.enable_link_integrity_checks
  True

  >>> editing_settings.lock_on_ttw_edit
  True


Language Control Panel
----------------------

  >>> from Products.CMFPlone.interfaces import ILanguageSchema
  >>> language_settings = registry.forInterface(ILanguageSchema, prefix='plone')

  >>> language_settings.default_language
  'en'

  >>> language_settings.available_languages
  ['en']

  >>> language_settings.use_combined_language_codes
  False

  >>> language_settings.display_flags
  False

  >>> language_settings.always_show_selector
  False

  >>> language_settings.use_content_negotiation
  False

  >>> language_settings.use_path_negotiation
  False

  >>> language_settings.use_cookie_negotiation
  False

  >>> language_settings.authenticated_users_only
  False

  >>> language_settings.set_cookie_always
  False

  >>> language_settings.use_subdomain_negotiation
  False

  >>> language_settings.use_cctld_negotiation
  False

  >>> language_settings.use_request_negotiation
  False


Maintenance Control Panel
-------------------------

  >>> from Products.CMFPlone.interfaces import IMaintenanceSchema
  >>> maintenance_settings = registry.forInterface(IMaintenanceSchema, prefix='plone')

  >>> maintenance_settings.days
  7


Navigation Control Panel
------------------------

  >>> from Products.CMFPlone.interfaces import INavigationSchema
  >>> navigation_settings = registry.forInterface(INavigationSchema, prefix='plone')

  >>> navigation_settings.generate_tabs
  True

  >>> navigation_settings.nonfolderish_tabs
  True

  >>> navigation_settings.displayed_types
  ('Image', 'File', 'Link', 'News Item', 'Folder', 'Document', 'Event')

  >>> navigation_settings.filter_on_workflow
  False

  >>> navigation_settings.workflow_states_to_show
  ()

  >>> navigation_settings.show_excluded_items
  True


Search Control Panel
--------------------

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> search_settings = registry.forInterface(ISearchSchema, prefix='plone')

  >>> search_settings.enable_livesearch
  False

  >>> search_settings.types_not_searched
  (...)


Site Control Panel
------------------

  >>> from Products.CMFPlone.interfaces import ISiteSchema
  >>> site_settings = registry.forInterface(ISiteSchema, prefix='plone')

  >>> site_settings.site_title
  u'Plone site'

  >>> site_settings.exposeDCMetaTags
  False

  >>> site_settings.enable_sitemap
  False

  >>> site_settings.webstats_js
  u''


Overview Control Panel
----------------------

  >>> from Products.CMFPlone.interfaces.controlpanel import IDateAndTimeSchema
  >>> tz_settings = registry.forInterface(IDateAndTimeSchema, prefix='plone')

  >>> tz_settings.portal_timezone = 'UTC'


Markup Control Panel
--------------------

  >>> from Products.CMFPlone.interfaces import IMarkupSchema
  >>> markup_settings = registry.forInterface(IMarkupSchema, prefix='plone')

  >>> markup_settings.default_type
  u'text/html'

  >>> markup_settings.allowed_types
  ('text/html', 'text/x-web-textile')


User and Groups Control Panel
------------------------------

  >>> from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
  >>> usergroups_settings = registry.forInterface(IUserGroupsSettingsSchema, prefix='plone')

  >>> usergroups_settings.many_groups
  False

  >>> usergroups_settings.many_users
  False
