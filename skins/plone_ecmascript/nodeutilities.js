
function wrapNode(node, wrappertype, wrapperclass){
    /* utility function to wrap a node in an arbitrary element of type "wrappertype"
     * with a class of "wrapperclass" */
    wrapper = document.createElement(wrappertype)
    wrapper.className = wrapperclass;
    innerNode = node.parentNode.replaceChild(wrapper,node);
    wrapper.appendChild(innerNode)
}
function nodeContained(innernode, outernode){
    // check if innernode is contained in outernode
    var node
    node = innernode.parentNode;
    while (node != document){
        if (node == outernode){
            return true; 
            break
            }
        node=node.parentNode
        }
    return false
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