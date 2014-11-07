Plone Controlpanel
==================

All control panel related settings are stored in plone.app.registry and
can be looked up like this::

  >>> from zope.component import getUtility
  >>> from plone.registry.interfaces import IRegistry
  >>> registry = getUtility(IRegistry)

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> search_settings = registry.forInterface(ISearchSchema, prefix='plone')

  >>> search_settings.enable_livesearch
  True

If you want to change the settings, just change the attribute::

  >>> search_settings.enable_livesearch = False


Editing Control Panel
---------------------

  >>> from Products.CMFPlone.interfaces import IEditingSchema
  >>> editing_settings = registry.forInterface(IEditingSchema, prefix='plone')

  >>> editing_settings.visible_ids = False
  >>> editing_settings.default_editor = u'TinyMCE'
  >>> editing_settings.ext_editor = False
  >>> editing_settings.enable_link_integrity_checks = False
  >>> editing_settings.lock_on_ttw = False


Maintenance Control Panel
-------------------------

  >>> from Products.CMFPlone.interfaces import IMaintenanceSchema
  >>> maintenance_settings = registry.forInterface(IMaintenanceSchema, prefix='plone')

  >>> maintenance_settings.days = 7


Navigation Control Panel
------------------------

  >>> from Products.CMFPlone.interfaces import INavigationSchema
  >>> navigation_settings = registry.forInterface(INavigationSchema, prefix='plone')

  >>> navigation_settings.generate_tabs = True
  >>> navigation_settings.nonfolderish_tabs = True
  >>> navigation_settings.displayed_types = ('Document', 'Folder')
  >>> navigation_settings.filter_on_workflow = False
  >>> navigation_settings.workflow_states_to_show = ()
  >>> navigation_settings.show_excluded_items = True


Search Control Panel
--------------------

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> search_settings = registry.forInterface(ISearchSchema, prefix='plone')

  >>> search_settings.enable_livesearch = True
  >>> search_settings.types_not_searched = ('Discussion Item', 'Folder')


Site Control Panel
------------------

  >>> from Products.CMFPlone.interfaces import ISiteSchema
  >>> site_settings = registry.forInterface(ISiteSchema, prefix='plone')

  >>> site_settings.site_title = u'My Site'
  >>> site_settings.description_title = u'This is my site'
  >>> site_settings.exposeDCMetaTags = True
  >>> site_settings.enable_sitemap = True
  >>> site_settings.webstats_js = u'<script>a=1</script>'


Overview Control Panel
----------------------

  >>> from Products.CMFPlone.interfaces.controlpanel import IDateAndTimeSchema
  >>> tz_settings = IDateAndTimeSchema(prefix='plone')
  >>> tz_settings.portal_timezone = 'UTC'
