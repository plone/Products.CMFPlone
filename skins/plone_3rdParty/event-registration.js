// this contains parts from:
// http://tanny.ica.com/ica/tko/tkoblog.nsf/dx/domcontentloaded-for-browsers-part-ii

// Array of DOMContentLoaded event handlers.
window.onDOMLoadEvents = new Array();
window.DOMContentLoadedInitDone = false;

// Function that adds DOMContentLoaded listeners to the array.
function addDOMLoadEvent(listener) {
    window.onDOMLoadEvents[window.onDOMLoadEvents.length]=listener;
}

// Function to process the DOMContentLoaded events array.
function DOMContentLoadedInit() {
    // quit if this function has already been called
    if (window.DOMContentLoadedInitDone) return;

    // flag this function so we don't do the same thing twice
    window.DOMContentLoadedInitDone = true;

    // iterates through array of registered functions 
    var exceptions = new Array();
    for (var i=0; i<window.onDOMLoadEvents.length; i++) {
        var func = window.onDOMLoadEvents[i];
        try {
            func();
        } catch(e) {
            // continue running init functions but save exceptions for later
            exceptions[exceptions.length] = e;
        }
    }
    for (var i=0; i<exceptions.length; i++) {
        throw exceptions[i];
    }
}

function DOMContentLoadedScheduler() {
    // quit if the init function has already been called
    if (window.DOMContentLoadedInitDone) return true;
    
    // Check for Safari/WebKit or KHTML
    if(/KHTML|WebKit/i.test(navigator.userAgent)) {
        if(/loaded|complete/.test(document.readyState)) {
            DOMContentLoadedInit();
        } else {
            // Not ready yet, wait a little more.
            setTimeout("DOMContentLoadedScheduler()", 250);
        }
    } else {
        // Not ready yet, wait a little more.
        setTimeout("DOMContentLoadedScheduler()", 250);
    }
    
    return true;
}

// Schedule to run the init function.
setTimeout("DOMContentLoadedScheduler()", 250);

// Just in case window.onload happens first, add it there too.
if (window.addEventListener) {
    window.addEventListener("load", DOMContentLoadedInit, false);
    // If addEventListener supports the DOMContentLoaded event.
    document.addEventListener("DOMContentLoaded", DOMContentLoadedInit, false);
} else if (window.attachEvent) {
    window.attachEvent("onload", DOMContentLoadedInit);
} else {
    var _dummy = function() {
        var $old_onload = window.onload;
        window.onload = function(e) {
            DOMContentLoadedInit();
            $old_onload();
        }
    }
}

/* for Internet Explorer */
/*@cc_on @*/
/*@if (@_win32)
{
    var proto = "src='javascript:void(0)'";
    if (location.protocol == "https:") proto = "src=//0";
    document.write("<scr"+"ipt id=__ie_onload defer " + proto + "><\/scr"+"ipt>");
    var script = document.getElementById("__ie_onload");
    script.onreadystatechange = function() {
        if (this.readyState == "complete") {
            DOMContentLoadedInit(); // call the onload handler
        }
    }
};
/*@end @*/
