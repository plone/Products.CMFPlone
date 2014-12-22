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

For more informations about how to access and manipulate Plone registry eintries, look at
the `plone.registry documentation
<https://github.com/plone/plone.registry/blob/master/plone/registry/registry.rst>`_:


Editing Control Panel
---------------------

  >>> from Products.CMFPlone.interfaces import IEditingSchema
  >>> editing_settings = registry.forInterface(IEditingSchema, prefix='plone')

  >>> editing_settings.visible_ids
  False
  >>> editing_settings.visible_ids = True

  >>> editing_settings.default_editor
  u'TinyMCE'
  >>> editing_settings.default_editor = u'TinyMCE'

  >>> editing_settings.ext_editor
  False
  >>> editing_settings.ext_editor = True

  >>> editing_settings.enable_link_integrity_checks
  True
  >>> editing_settings.enable_link_integrity_checks = False

  >>> editing_settings.lock_on_ttw_edit
  True
  >>> editing_settings.lock_on_ttw_edit = False


Maintenance Control Panel
-------------------------

  >>> from Products.CMFPlone.interfaces import IMaintenanceSchema
  >>> maintenance_settings = registry.forInterface(IMaintenanceSchema, prefix='plone')

  >>> maintenance_settings.days
  7
  >>> maintenance_settings.days = 1


Navigation Control Panel
------------------------

  >>> from Products.CMFPlone.interfaces import INavigationSchema
  >>> navigation_settings = registry.forInterface(INavigationSchema, prefix='plone')

  >>> navigation_settings.generate_tabs
  True
  >>> navigation_settings.generate_tabs = False

  >>> navigation_settings.nonfolderish_tabs
  True
  >>> navigation_settings.nonfolderish_tabs = False

  >>> navigation_settings.displayed_types
  ('Image', 'File', 'Link', 'News Item', 'Folder', 'Document', 'Event')
  >>> navigation_settings.displayed_types = ('Document', 'Folder')

  >>> navigation_settings.filter_on_workflow
  False
  >>> navigation_settings.filter_on_workflow = True

  >>> navigation_settings.workflow_states_to_show
  ()
  >>> navigation_settings.workflow_states_to_show = ()

  >>> navigation_settings.show_excluded_items
  True
  >>> navigation_settings.show_excluded_items = False


Search Control Panel
--------------------

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> search_settings = registry.forInterface(ISearchSchema, prefix='plone')

  >>> search_settings.enable_livesearch
  False
  >>> search_settings.enable_livesearch = True

  >>> search_settings.types_not_searched
  (...)
  >>> search_settings.types_not_searched = ('Discussion Item', 'Folder')


Site Control Panel
------------------

  >>> from Products.CMFPlone.interfaces import ISiteSchema
  >>> site_settings = registry.forInterface(ISiteSchema, prefix='plone')

  >>> site_settings.site_title
  u'Plone site'
  >>> site_settings.site_title = u'My Site'

  >>> site_settings.exposeDCMetaTags
  False
  >>> site_settings.exposeDCMetaTags = True

  >>> site_settings.enable_sitemap
  False
  >>> site_settings.enable_sitemap = True

  >>> site_settings.webstats_js
  u''
  >>> site_settings.webstats_js = u'<script>a=1</script>'


Overview Control Panel
----------------------

  >>> from Products.CMFPlone.interfaces.controlpanel import IDateAndTimeSchema
  >>> tz_settings = registry.forInterface(IDateAndTimeSchema, prefix='plone')
  >>> tz_settings.portal_timezone = 'UTC'


Markup Control Panel
------------------------

  >>> from Products.CMFPlone.interfaces import IMarkupSchema
  >>> markup_settings = registry.forInterface(IMarkupSchema, prefix='plone')

  >>> markup_settings.default_type = 'text/html'
  >>> markup_settings.allowed_types = ('text/html', 'text/x-web-textile')


User and Groups Control Panel
------------------

  >>> from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
  >>> usergroups_settings = registry.forInterface(IUserGroupsSettingsSchema, prefix='plone')

  >>> usergroups_settings.many_groups = False
  >>> usergroups_settings.many_users = False
