
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
    if (node.className) {
        class_names = node.className.split(' ');
        for (class_index in class_names) {
            if (class_names[class_index] == class_name){
                return true;
            }
        }
    }
    return false;
}

function addClassName(node, class_name) {
    if (!hasClassName(node, class_name)) {
        node.className += " "+class_name;
    }
}

function removeClassName(node, class_name) {
    if (node.className) {
        class_names = node.className.split(' ');
        var new_classes = new Array();
        for (class_index in class_names) {
            cn = class_names[class_index];
            if (cn != class_name) {
                new_classes.push(cn);
            }
        }
        node.className = new_classes.join(" ");
    }
}

function replaceClassName(node, old_class, new_class, ignore_missing) {
    if (node.className) {
        class_names = node.className.split(' ');
        var new_classes = new Array();
        var found_old = false;
        for (class_index in class_names) {
            cn = class_names[class_index];
            if (cn == old_class) {
                found_old = true;
                continue;
            } else if (cn != new_class) {
                new_classes.push(cn);
            }
        }
        if (found_old || ignore_missing) {
            new_classes.push(new_class);
        }
        node.className = new_classes.join(" ");
    }
}

/*
function jscss(a,o,c1,c2)
{
  switch (a){
    case 'swap':
      o.className=!jscss('check',o,c1)?o.className.replace(c2,c1): <-
      o.className.replace(c1,c2);
    break;
    case 'add':
      if(!jscss('check',o,c1)){o.className+=o.className?' '+c1:c1;}
    break;
    case 'remove':
      var rep=o.className.match(' '+c1)?' '+c1:c1;
      o.className=o.className.replace(rep,'');
    break;
    case 'check':
      return new RegExp('\\b'+c1+'\\b').test(o.className)
    break;
  }
}
*/
