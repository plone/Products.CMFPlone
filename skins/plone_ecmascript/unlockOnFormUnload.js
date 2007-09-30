/* Unlock the object on form unload*/
$(function() {
    // set up the handler, if there are any forms
    if ($('form.enableUnlockProtection').length)
        $(window).unload(function() {
            var baseUrl = $('base').attr('href');
            if (!baseUrl) {
                var pieces = window.location.href.split('/');
                pieces.pop();
                baseUrl = pieces.join('/');
            }
            $.get(baseUrl + '/@@plone_lock_operations/safe_unlock');
        });
});
