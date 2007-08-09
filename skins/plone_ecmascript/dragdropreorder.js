var ploneDnDReorder = {}

ploneDnDReorder.dragging = null;
ploneDnDReorder.table = null;
ploneDnDReorder.rows = null;

ploneDnDReorder.isDraggable = function(node) {
    return hasClassName(node, 'draggable');
};

ploneDnDReorder.doDown = function(e) {
    if (!e) var e = window.event; // IE compatibility
    var target = findContainer(this, ploneDnDReorder.isDraggable);
    if (target == null)
        return;
    for (var i=0; i<ploneDnDReorder.rows.length; i++)
        ploneDnDReorder.rows[i].onmousemove = ploneDnDReorder.doDrag;


    ploneDnDReorder.dragging = target.parentNode;
    var dragging = ploneDnDReorder.dragging;
    dragging._position = ploneDnDReorder.getPos(dragging);
    addClassName(dragging, "dragging");
    return false;
}

ploneDnDReorder.getPos = function(node) {
    var children = node.parentNode.childNodes;
    var pos = 0;
    for (var i=0; i<children.length; i++) {
        if (node == children[i])
            return pos;
        if (hasClassName(children[i], "draggable"))
            pos++;
    }
    return null;
}

ploneDnDReorder.doDrag = function(e) {
    if (!e) var e = window.event; // IE compatibility

    var dragging = ploneDnDReorder.dragging;
    if (!dragging)
        return;
    var target = this;
    if (!target)
        return;

    if (target.id != dragging.id) {
        ploneDnDReorder.swapElements(target, dragging);
    }
    return false;
}

ploneDnDReorder.swapElements = function(child1, child2) {
    // currently, this works by building a list of all the
    // children, swapping the elements in this list, then
    // removing all the children and replacing them with our
    // list. there must be a more efficient way, but other approaches
    // i tried were buggy.
    var parent = child1.parentNode;
    var children = parent.childNodes;
    var items = new Array();
    for (var i = 0; i < children.length; i++) {
        var node = children[i];
        items[i] = node;
        if (node.id) {
            removeClassName(node, "even");
            removeClassName(node, "odd");
            if (node.id == child1.id)
                items[i] = child2;
            if (node.id == child2.id)
                items[i] = child1;
        }
    }
    Sarissa.clearChildNodes(parent);
    var pos = 0;
    for (var i = 0; i < items.length; i++) {
        var node = parent.appendChild(items[i]);
        if (node.id) {
            if (pos % 2)
                addClassName(node, "even");
            else
                addClassName(node, "odd");
            pos++;
        }
    }
}

ploneDnDReorder.doUp = function(e) {
    if (!e) var e = window.event; // IE compatibility

    var dragging = ploneDnDReorder.dragging;
    if (!dragging)
        return;

    removeClassName(dragging, "dragging");
    ploneDnDReorder.updatePositionOnServer();
    dragging._position = null;
    try {
        delete dragging._position;
    } catch(e) {}
    dragging = null;
    for (var i=0; i<ploneDnDReorder.rows.length; i++)
        ploneDnDReorder.rows[i].onmousemove = null;
    return false;
}

ploneDnDReorder.updatePositionOnServer = function() {
    var dragging = ploneDnDReorder.dragging;
    var delta = ploneDnDReorder.getPos(dragging) - dragging._position;

    if (delta == 0) // nothing changed
        return;
    var req = new XMLHttpRequest();
    req.open("POST", "folder_moveitem", true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    // Strip off id prefix
    var item_id = dragging.id.substr('folder-contents-item-'.length);
    req.send("item_id="+item_id+"&delta:int="+delta);
}

