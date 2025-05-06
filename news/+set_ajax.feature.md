Automatically set the ajax_load request parameter.

Zope maintains the "HTTP_X_REQUESTED_WITH" request header. If this is set to
"XMLHttpRequest", we have an AJAX request. In this case the ajax_load parameter
is set to True directly on the request object.
If the ajax_load parameter was already set to a true-ish or false-ish value, it
is not overwritten.

This should make use for the ajax_main_template for any AJAX request,
regardless if the ajax_load parameter was manually set or not and potentially
speed up Plone Classic UI rendering.
