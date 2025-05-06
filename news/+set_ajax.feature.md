Automatically set the ajax_load request parameter.

Most JavaScript libraries send the "HTTP_X_REQUESTED_WITH" request header set
to "XMLHttpRequest" for AJAX requests. For AJAX requests we set the "ajax_load"
parameter on the request object before traversing, if it was not already set.

This is further used to switch to the ajax_main_template and to turn off Diazo
transformations.

For AJAX requests which need a full-page rendering this automatic setting can
be turned off by adding `?ajax_load=0` as query string to the URL.
