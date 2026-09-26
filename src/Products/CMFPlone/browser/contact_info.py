import zope.deferredimport

zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Import from plone.app.layout.views.contact_info instead. "
    "This will be removed in Plone 7.",
    ContactForm="plone.app.layout.views.contact_info:ContactForm",
)
