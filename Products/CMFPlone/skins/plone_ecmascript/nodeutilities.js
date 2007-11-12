
function wrapNode(node, wrappertype, wrapperclass){
    /* utility function to wrap a node in an arbitrary element of type "wrappertype"
     * with a class of "wrapperclass" */
    var wrapper = document.createElement(wrappertype)
    wrapper.className = wrapperclass;
    var innerNode = node.parentNode.replaceChild(wrapper,node);
    wrapper.appendChild(innerNode);
};

function nodeContained(innernode, outernode){
    // check if innernode is contained in outernode
    var node = innernode.parentNode;
    while (node != document) {
        if (node == outernode) {
            return true; 
        }
        node=node.parentNode;
    }
    return false;
};

function findContainer(node, func) {
    // Starting with the given node, find the nearest containing element
    // for which the given function returns true.

    while (node != null) {
        if (func(node)) {
            return node;
        }
        node = node.parentNode;
    }
    return false;
};

function hasClassName(node, class_name) {
    return new RegExp('\\b'+class_name+'\\b').test(node.className);
};

function addClassName(node, class_name) {
    if (!node.className) {
        node.className = class_name;
    } else if (!hasClassName(node, class_name)) {
        var className = node.className+" "+class_name;
        // cleanup
        node.className = className.split(/\s+/).join(' ');
    }
};

function removeClassName(node, class_name) {
    var className = node.className;
    if (className) {
        // remove
        className = className.replace(new RegExp('\\b'+class_name+'\\b'), '');
        // cleanup
        className = className.replace(/\s+/g, ' ');
        node.className = className.replace(/\s+$/g, '');
    }
};

function replaceClassName(node, old_class, new_class, ignore_missing) {
    if (ignore_missing && !hasClassName(node, old_class)) {
        addClassName(node, new_class);
    } else {
        var className = node.className;
        if (className) {
            // replace
            className = className.replace(new RegExp('\\b'+old_class+'\\b'), new_class);
            // cleanup
            className = className.replace(/\s+/g, ' ');
            node.className = className.replace(/\s+$/g, '');
        }
    }
};

function walkTextNodes(node, func, data) {
    // traverse childnodes and call func when a textnode is found
    if (!node){return false}
    if (node.hasChildNodes) {
        // we can't use for (i in childNodes) here, because the number of
        // childNodes might change (higlightsearchterms)
        for (var i=0;i<node.childNodes.length;i++) {
            walkTextNodes(node.childNodes[i], func, data);
        }
        if (node.nodeType == 3) {
            // this is a text node
            func(node, data);
        }
    }
};

/* These are two functions, because getInnerTextFast doesn't always return the
 * the same results, as it depends on the implementation of node.innerText of
 * the browser. getInnerTextCompatible will always return the same values, but
 * is a bit slower. The difference is just in the whitespace, so if this
 * doesn't matter, you should always use getInnerTextFast.
 */

function getInnerTextCompatible(node) {
    var result = new Array();
    walkTextNodes(node,
                  function(n, d){d.push(n.nodeValue)},
                  result);
    return result.join("");
};

function getInnerTextFast(node) {
    if (node.innerText) {
        return node.innerText;
    } else {
        return getInnerTextCompatible(node);
    }
};

/* This function reorder nodes in the DOM.
 * fetch_func - the function which returns the value for comparison
 * cmp_func - the compare function, if not provided then the string of the
 * value returned by fetch_func is used.
 */
function sortNodes(nodes, fetch_func, cmp_func) {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    // wrapper for sorting
    var SortNodeWrapper = function(node) {
        this.value = fetch_func(node);
        this.cloned_node = node.cloneNode(true);
        this.toString = function() {
            if (this.value.toString) {
                return this.value.toString();
            } else {
                return this.value;
            }
        }
    }

    // wrap nodes
    var items = new Array();
    for (var i=0; i<nodes.length; i++) {
        items.push(new SortNodeWrapper(nodes[i]));
    }

    //sort
    if (cmp_func) {
        items.sort(cmp_func);
    } else {
        items.sort();
    }

    // reorder nodes
    for (var i=0; i<items.length; i++) {
        var dest = nodes[i];
        dest.parentNode.replaceChild(items[i].cloned_node, dest);
    }
};

function copyChildNodes(srcNode, dstNode) {
    var nodes = srcNode.childNodes;
    for (var i=0; i<nodes.length; i++) {
        dstNode.appendChild(nodes[i].cloneNode(true));
    }
}
