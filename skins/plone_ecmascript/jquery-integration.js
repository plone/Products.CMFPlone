// If cssQuery is not defined (loaded earlier), redefine it in terms of jQuery
// For everything but corner cases, this is good enough
if (typeof cssQuery == 'undefined')
    function cssQuery(s, f) { return $.makeArray($(s, f)) };
