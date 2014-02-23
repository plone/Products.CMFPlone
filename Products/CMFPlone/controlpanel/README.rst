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


Search Control Panel
--------------------

  >>> from Products.CMFPlone.interfaces import ISearchSchema
  >>> site_settings = registry.forInterface(ISearchSchema, prefix='plone')

  >>> site_settings.enable_livesearch = True
  >>> site_settings.types_not_searched = ('Discussion Item', 'Folder')


Site Control Panel
------------------

  >>> from Products.CMFPlone.interfaces import ISiteSchema
  >>> site_settings = registry.forInterface(ISiteSchema, prefix='plone')

  >>> site_settings.site_title = u'My Site'
  >>> site_settings.description_title = u'This is my site'
  >>> site_settings.exposeDCMetaTags = True
  >>> site_settings.enable_sitemap = True
  >>> site_settings.webstats_js = u'<script>a=1</script>'
