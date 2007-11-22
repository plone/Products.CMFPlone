/* Unlock the object on form unload*/

if (typeof(plone)=='undefined'){
    var plone = {};
}

if (window.onunload) {
    throw "Attempt to redefine window.unonload (not supported)";
}

plone.dummyProcessReqChange = function() {};
plone.UnlockHandler = function() {
    var self = this;

    this.execute = function(event) {
        // this.submitting is set from the form unload handler
        // (formUnload.js) and signifies that we are in the
        // form submit process. This means: no unlock needed,
        // and it also would be harmful (ConflictError)
        if (self.submitting) {
             return;
        }
        var objectUrl = "";
        var baseUrl = undefined;
        var nodes = document.getElementsByTagName("base");
        if (nodes.length == 0) {
            var base = window.location.href;
            var pieces = base.split('/');
            pieces.pop();
            baseUrl = pieces.join('/');
        } else {
            baseUrl = nodes[0].href;
        }
        var unlockRequest = new XMLHttpRequest();
        unlockRequest.onreadystatechange= plone.dummyProcessReqChange;
        unlockRequest.open("GET", baseUrl + "/@@plone_lock_operations/safe_unlock");
        unlockRequest.send(null);
    };
    this.execute.tool = this;
};

//var Class = UnlockHandler.prototype;

registerPloneFunction(function() {
    // Check if there are any forms
    var forms = cssQuery('form.enableUnlockProtection');

    // set up the handler, if there are any forms
    if (forms.length > 0) {
        var handler = new plone.UnlockHandler().execute;
        window.onunload = handler;
    }
});
