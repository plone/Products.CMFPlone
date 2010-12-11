// These methods have all been deprecated in favor of using jquery.

/*
  Provides globals:

  addClassName, copyChildNodes, findContainer, getInnerTextCompatible, 
  getInnerTextFast, hasClassName, nodeContained, removeClassName, 
  replaceClassName, sortNodes, walkTextNodes, wrapNode
*/

function wrapNode(node, wrappertype, wrapperclass){
    /* utility function to wrap a node in an arbitrary element of type "wrappertype"
     * with a class of "wrapperclass" */
    jQuery(node).wrap('<' + wrappertype + '>').parent().addClass(wrapperclass);
}

function nodeContained(innernode, outernode){
    // check if innernode is contained in outernode
    return jQuery(innernode).parents()
        .filter(function() { return this === outernode; }).length > 0;
}

function findContainer(node, func) {
    // Starting with the given node, find the nearest containing element
    // for which the given function returns true.
    var p = jQuery(node).parents().filter(func);
    return p.length ? p.get(0) : false;
}

function hasClassName(node, class_name) {
    return jQuery(node).hasClass(class_name);
}

function addClassName(node, class_name) {
    jQuery(node).addClass(class_name);
}

function removeClassName(node, class_name) {
    jQuery(node).removeClass(class_name);
}

function replaceClassName(node, old_class, new_class, ignore_missing) {
    if (ignore_missing || jQuery(node).hasClass(old_class)) {
        jQuery(node).removeClass(old_class).addClass(new_class);
    }
}

function walkTextNodes(node, func, data) {
    // find all nodes, and call a function for all it's textnodes
    jQuery(node).find('*').andSelf().contents().each(function() {
        if (this.nodeType === 3) {
            func(this, data);
        }
    });
}

function getInnerTextCompatible(node) {
    return jQuery(node).text();
}

function getInnerTextFast(node) {
    return jQuery(node).text();
}

/* This function reorder nodes in the DOM.
 * fetch_func - the function which returns the value for comparison
 * cmp_func - the compare function, if not provided then the string of the
 * value returned by fetch_func is used.
 */
function sortNodes(nodes, fetch_func, cmp_func) {
    // wrapper for sorting
    var SortNodeWrapper,
        items;

    SortNodeWrapper = function(node) {
        this.value = fetch_func(node);
        this.cloned_node = node.cloneNode(true);
    };
    SortNodeWrapper.prototype.toString = function() {
        return this.value.toString ? this.value.toString() : this.value;
    };

    // wrap nodes
    items = jQuery(nodes).map(function() { return new SortNodeWrapper(this); });

    //sort
    if (cmp_func) {
        items.sort(cmp_func);
    } else {
       items.sort();
    }

    // reorder nodes
    jQuery.each(items, function(i) { jQuery(nodes[i]).replace(this.cloned_node); });
}

function copyChildNodes(srcNode, dstNode) {
    jQuery(srcNode).children().clone().appendTo(jQuery(dstNode));
}
