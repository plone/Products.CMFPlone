/* Unlock the object on form unload*/
if (typeof(plone)=='undefined')
    var plone = {};

plone.UnlockHandler = {
    init: function() {
        // set up the handler, if there are any forms
        if ($('form.enableUnlockProtection').length)
            $(window).unload(plone.UnlockHandler.execute);
    },
    
    execute: function() {
        var baseUrl = $('base').attr('href');
        if (!baseUrl) {
            var pieces = window.location.href.split('/');
            pieces.pop();
            baseUrl = pieces.join('/');
        }
        $.get(baseUrl + '/@@plone_lock_operations/safe_unlock');
    }
};

$(plone.UnlockHandler.init);
