/* Essential javascripts, used a lot. 
 * These should be placed inline
 * We have to be certain they are loaded before anything that uses them 
 */

// check for ie5 mac
var bugRiddenCrashPronePieceOfJunk = (
    navigator.userAgent.indexOf('MSIE 5') != -1
    &&
    navigator.userAgent.indexOf('Mac') != -1
)

// check for W3CDOM compatibility
var W3CDOM = (!bugRiddenCrashPronePieceOfJunk &&
               document.getElementsByTagName &&
               document.createElement);

// cross browser function for registering event handlers
if (typeof addEvent != 'undefined') {
    // use Dean Edwards' function if available
    function registerEventListener(elem, event, func) {
        addEvent(elem, event, func);
        return true;
    }
} else if (window.addEventListener) {
    function registerEventListener(elem, event, func) {
        elem.addEventListener(event, func, false);
        return true;
    }
} else if (window.attachEvent) {
    function registerEventListener(elem, event, func) {
        var result = elem.attachEvent("on"+event, func);
        return result;
    }
} else {
    function registerEventListener(elem, event, func) {
        // maybe we could implement something with an array
        return false;
    }
}

// cross browser function for unregistering event handlers
if (typeof removeEvent != 'undefined') {
    // use Dean Edwards' function if available
    function unRegisterEventListener(elem, event, func) {
        removeEvent(element, event, func);
        return true;
    }
} else if (window.removeEventListener) {
    function unRegisterEventListener(elem, event, func) {
        elem.removeEventListener(event, func, false);
        return true;
    }
} else if (window.detachEvent) {
    function unRegisterEventListener(elem, event, func) {
        var result = elem.detachEvent("on"+event, func);
        return result;
    }
} else {
    function unRegisterEventListener(elem, event, func) {
        // maybe we could implement something with an array
        return false;
    }
}

if (typeof addDOMLoadEvent != 'undefined') {
    function registerPloneFunction(func) {
        // registers a function to fire onload.
        registerEventListener(window, "domload", func);
    }
} else {
    function registerPloneFunction(func) {
        // registers a function to fire onload.
        registerEventListener(window, "load", func);
    }
}

function getContentArea() {
    // returns our content area element
    if (W3CDOM) {
        var node = document.getElementById('region-content');
        if (!node) {
            node = document.getElementById('content');
        }
        return node;
    }
} 
