/* Unlock the object on form unload*/
if (typeof(plone)=='undefined')
    var plone = {};

plone.UnlockHandler = {    
    init: function() {
        // set up the handler, if there are any forms
        if (jq('form.enableUnlockProtection').length)
            jq(window).unload(plone.UnlockHandler.execute);
    },
    
    execute: function() {
        // this.submitting is set from the form unload handler
        // (formUnload.js) and signifies that we are in the
        // form submit process. This means: no unlock needed,
        // and it also would be harmful (ConflictError)
        if (this.submitting) return;

        var baseUrl = jq('base').attr('href');
        if (!baseUrl) {
            var pieces = window.location.href.split('/');
            pieces.pop();
            baseUrl = pieces.join('/');
        }
        jq.get(baseUrl + '/@@plone_lock_operations/safe_unlock');
    }
};

jq(plone.UnlockHandler.init);
