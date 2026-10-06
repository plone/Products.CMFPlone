import zope.deferredimport

zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Import from plone.app.layout.views.author instead. "
    "This will be removed in Plone 7.",
    AuthorFeedbackForm="plone.app.layout.views.author:AuthorFeedbackForm",
    AuthorView="plone.app.layout.views.author:AuthorView",
)
