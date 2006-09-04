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
               typeof document.getElementsByTagName != 'undefined' &&
               typeof document.createElement != 'undefined' );

// cross browser function for registering event handlers
var registerEventListener = undefined;

if (typeof addEvent != 'undefined') {
    // use Dean Edwards' function if available
    registerEventListener = function (elem, event, func) {
        addEvent(elem, event, func);
        return true;
    }
} else if (window.addEventListener) {
    registerEventListener = function (elem, event, func) {
        elem.addEventListener(event, func, false);
        return true;
    }
} else if (window.attachEvent) {
    registerEventListener = function (elem, event, func) {
        var result = elem.attachEvent("on"+event, func);
        return result;
    }
} else {
    registerEventListener = function (elem, event, func) {
        // maybe we could implement something with an array
        return false;
    }
}

// cross browser function for unregistering event handlers
var unRegisterEventListener = undefined;

if (typeof removeEvent != 'undefined') {
    // use Dean Edwards' function if available
    unRegisterEventListener = function (elem, event, func) {
        removeEvent(element, event, func);
        return true;
    }
} else if (window.removeEventListener) {
    unRegisterEventListener = function (elem, event, func) {
        elem.removeEventListener(event, func, false);
        return true;
    }
} else if (window.detachEvent) {
    unRegisterEventListener = function (elem, event, func) {
        var result = elem.detachEvent("on"+event, func);
        return result;
    }
} else {
    unRegisterEventListener = function (elem, event, func) {
        // maybe we could implement something with an array
        return false;
    }
}

var registerPloneFunction = undefined;

if (typeof addDOMLoadEvent != 'undefined') {
    registerPloneFunction = function (func) {
        // registers a function to fire ondomload.
        registerEventListener(window, "domload", func);
    }
} else {
    registerPloneFunction = function (func) {
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
