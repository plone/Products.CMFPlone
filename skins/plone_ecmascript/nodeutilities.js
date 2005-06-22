
function wrapNode(node, wrappertype, wrapperclass){
    /* utility function to wrap a node in an arbitrary element of type "wrappertype"
     * with a class of "wrapperclass" */
    wrapper = document.createElement(wrappertype)
    wrapper.className = wrapperclass;
    innerNode = node.parentNode.replaceChild(wrapper,node);
    wrapper.appendChild(innerNode);
}

function nodeContained(innernode, outernode){
    // check if innernode is contained in outernode
    var node;
    node = innernode.parentNode;
    while (node != document) {
        if (node == outernode) {
            return true; 
        }
        node=node.parentNode;
    }
    return false;
}

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
}

function hasClassName(node, class_name) {
    return new RegExp('\\b'+class_name+'\\b').test(node.className);
}

function addClassName(node, class_name) {
    if (!node.className) {
        node.className = class_name;
    } else if (!hasClassName(node, class_name)) {
        var className = node.className+" "+class_name;
        // cleanup
        node.className = className.split(/\s+/).join(' ');
    }
}

function removeClassName(node, class_name) {
    var className = node.className;
    if (className) {
        // remove
        className = className.replace(new RegExp('\\b'+class_name+'\\b'), '');
        // cleanup
        className = className.replace(/\s+/g, ' ');
        node.className = className.replace(/\s+$/g, '');
    }
}

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
}

function walkTextNodes(node, func, data) {
    // traverse childnodes and call func when a textnode is found
    if (!node){return false}
    if (node.hasChildNodes) {
        var i;
        // we can't use for (i in childNodes) here, because the number of
        // childNodes might change (higlightsearchterms)
        for (i=0;i<node.childNodes.length;i++) {
            walkTextNodes(node.childNodes[i], func, data);
        }
        if (node.nodeType == 3) {
            // this is a text node
            func(node, data);
        }
    }
}

function getInnerTextCompatible(node) {
    var result = new Array();
    walkTextNodes(node,
                  function(n, d){d.push(n.nodeValue)},
                  result);
    return result.join("");
}

function getInnerTextFast(node) {
    if (node.innerText) {
        return node.innerText;
    } else {
        return getInnerTextCompatible(node);
    }
}