
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

function textTraverse(node, result) {
    // traverse childnodes
    if (!node){return false}
    if (node.hasChildNodes) {
        var i;
        for (i in node.childNodes) {
            textTraverse(node.childNodes[i], result);
        }
        if (node.nodeType == 3) {
            // this is a text node
            result.push(node.nodeValue);
        }
    }
}

function getInnerTextCompatible(node) {
    var result = new Array();
    textTraverse(node, result);
    return result.join("");
}

function getInnerTextFast(node) {
    if (node.innerText) {
        return node.innerText;
    } else {
        return getInnerTextCompatible(node);
    }
}