// DEPRECATION WARNING: The jq alias will be removed in Plone 5.
// Do not use jq(), but use proper wrapping. 
// See http://docs.jquery.com/Plugins/Authoring#Custom_Alias
var jq = jQuery;

// If cssQuery is not defined (loaded earlier), redefine it in terms of jQuery
// For everything but corner cases, this is good enough
if (typeof cssQuery == 'undefined') {
    function cssQuery(s, f) { return jQuery.makeArray(jQuery(s, f)) };
};

// load jQuery Plone plugins on load
(function($) {
    $(function() {
        // Highlight search results, but ignore referrals from our own domain
        // when displaying search results.
        $('#region-content,#content').highlightSearchTerms({
            includeOwnDomain: $('dl.searchResults').length == 0
        });
    });
})(jQuery);
