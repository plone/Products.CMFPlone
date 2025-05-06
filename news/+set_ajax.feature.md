Automatically set the ajax_load request parameter.

Zope maintains the "HTTP_X_REQUESTED_WITH" request header.
If this is set to "XMLHttpRequest", we have an AJAX request.
If so, the ajax_load parameter is set to "true", regardless if it was set
manually or not.

This should make use for the ajax_main_template for any AJAX request,
potentially speeding up classic Plone by avoiding loading unnecessary stuff.
