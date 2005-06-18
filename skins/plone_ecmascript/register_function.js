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
function registerEventListener(elem, event, func) {
    if (elem.addEventListener) {
        elem.addEventListener(event, func, false);
        return true;
    } else if (elem.attachEvent) {
        var result = elem.attachEvent("on"+event, func);
        return result;
    }
    // maybe we could implement something with an array
    return false;
}

// cross browser function for unregistering event handlers
function unRegisterEventListener(elem, event, func) {
    if (elem.removeEventListener) {
        elem.removeEventListener(event, func, false);
        return true;
    } else if (elem.detachEvent) {
        var result = elem.detachEvent("on"+event, func);
        return result;
    }
    // maybe we could implement something with an array
    return false;
}

function registerPloneFunction(func) {
    // registers a function to fire onload.
    registerEventListener(window, "load", func);
}

function unRegisterPloneFunction(func) {
    // unregisters a function so it does not fire onload.
    unRegisterEventListener(window, "load", func);
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
