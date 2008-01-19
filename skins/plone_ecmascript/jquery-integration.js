// To avoid conflicts, use the 'jq' variable instead of the $ variable
var jq = jQuery.noConflict();

// If cssQuery is not defined (loaded earlier), redefine it in terms of jQuery
// For everything but corner cases, this is good enough
if (typeof cssQuery == 'undefined') {
    function cssQuery(s, f) { return jq.makeArray(jq(s, f)) };
};
