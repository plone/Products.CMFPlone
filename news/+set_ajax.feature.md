Automatically use the ajax main template for XHR requests, if set.

If the `plone.use_ajax_main_template` registry parameter is set to True, a XHR
request is detected and the `ajax_load` does not evaluate to `False`, the ajax
main template is used automatically for XHR requests.

This can potentially speed up sites with a lot of AJAX requests.
