Plone Controlpanel
==================

All control panel related settings are stored in plone.app.registry and
can be looked up like this::

  >>> from zope.component import getUtility
  >>> from plone.registry.interfaces import IRegistry
  >>> registry = getUtility(IRegistry)

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> search_settings = registry.forInterface(ISearchSchema)

  >>> site_settings.enable_livesearch
  True

If you want to change the settings, just change the attribute::

  >>> search_settings.enable_livesearch = False


Search Control Panel
--------------------

  >>> from plone.app.controlpanel.interfaces import ISearchSchema
  >>> site_settings = registry.forInterface(ISearchSchema)

  >>> site_settings.enable_livesearch = True
  >>> site_settings.types_not_searched = ('Discussion Item', 'Folder')
