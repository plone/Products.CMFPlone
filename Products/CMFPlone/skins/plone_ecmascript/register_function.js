/* 
  Deprecated utility functions - Use jQuery directly instead.
  These will be gone in Plone 5.
*/

/*
  Provides globals:
  W3CDOM, bugRiddenCrashPronePieceOfJunk, getContentArea, 
  registerEventListener, registerPloneFunction, unRegisterEventListener
*/  

/*global navigator */


// check for ie5 mac
var bugRiddenCrashPronePieceOfJunk = (
    navigator.userAgent.indexOf('MSIE 5') !== -1 && navigator.userAgent.indexOf('Mac') !== -1
);

// check for W3CDOM compatibility
var W3CDOM = (!bugRiddenCrashPronePieceOfJunk &&
               typeof document.getElementsByTagName !== 'undefined' &&
               typeof document.createElement !== 'undefined' );

// cross browser function for registering event handlers
var registerEventListener = function(elem, event, func) {
    jQuery(elem).bind(event, func);
};

// cross browser function for unregistering event handlers
var unRegisterEventListener = function(elem, event, func) {
    jQuery(elem).unbind(event, func);
};

var registerPloneFunction = jQuery;

function getContentArea() {
    // returns our content area element
    var node = jQuery('#region-content,#content');
    return node.length ? node[0] : null;
} 
