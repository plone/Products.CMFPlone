
function wrapNode(node, wrappertype, wrapperclass){
    // utility function to wrap a node "node" in an arbitrary element of type "wrappertype" , with a class of "wrapperclass"
    wrapper = document.createElement(wrappertype)
    wrapper.className = wrapperclass;
    innerNode = node.parentNode.replaceChild(wrapper,node);
    wrapper.appendChild(innerNode)
}
  
function nodeContained(innernode, outernode){
    // check if innernode is contained in outernode
    var node
    //debugger
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
