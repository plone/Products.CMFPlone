/*
    Provides globals jq and cssQuery; Both are deprecated and are provided
    only for backwards compatibility.
    
    DEPRECATION WARNING: The jq alias will be removed in Plone 5.
    Do not use jq(), but use proper wrapping. 
    See http://docs.jquery.com/Plugins/Authoring#Custom_Alias
*/

/*global cssQuery:true */

var jq = jQuery;

// If cssQuery is not defined (loaded earlier), redefine it in terms of jQuery
// For everything but corner cases, this is good enough
if (typeof cssQuery === 'undefined') {
    var cssQuery = function (s, f) { return jQuery.makeArray(jQuery(s, f)); };
}
