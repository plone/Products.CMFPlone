When enabled, use the ajax main template for XHR requests.

If the ``plone.use_ajax_main_template`` registry setting is set to ``True``,
and an XHR request is detected where the ``ajax_load`` query string parameter
does not evaluate to ``False``, the system will automatically use the AJAX main
template for that request.

This can improve performance on sites that handle a large number of AJAX requests.
