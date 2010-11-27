var ploneDnDReorder = {};

ploneDnDReorder.dragging = null;
ploneDnDReorder.table = null;
ploneDnDReorder.rows = null;

(function($) {

ploneDnDReorder.doDown = function(e) {
    var dragging =  $(this).parents('.draggable:first');
    if (!dragging.length) return;
    ploneDnDReorder.rows.mousemove(ploneDnDReorder.doDrag);

    ploneDnDReorder.dragging = dragging;
    dragging._position = ploneDnDReorder.getPos(dragging);
    dragging.addClass("dragging");
    $(this).parents('tr').addClass('dragindicator');

    return false;
};

ploneDnDReorder.getPos = function(node) {
    var pos = node.parent().children('.draggable').index(node[0]);
    return pos == -1 ? null : pos;
};

ploneDnDReorder.doDrag = function(e) {
    var dragging = ploneDnDReorder.dragging;
    if (!dragging) return;
    var target = this;
    if (!target) return;

    if ($(target).attr('id') != dragging.attr('id')) {
        ploneDnDReorder.swapElements($(target), dragging);
    };
    return false;
};

ploneDnDReorder.swapElements = function(child1, child2) {
    var parent = child1.parent();
    var items = parent.children('[id]');
    items.removeClass('even').removeClass('odd');
    if (child1[0].swapNode) {
        // IE proprietary method
        child1[0].swapNode(child2[0]);
    } else {
        // swap the two elements, using a textnode as a position marker
        var t = parent[0].insertBefore(document.createTextNode(''),
                                       child1[0]);
        child1.insertBefore(child2);
        child2.insertBefore(t);
        $(t).remove();
    };
    // odd and even are 0-based, so we want them the other way around
    parent.children('[id]:odd').addClass('even');
    parent.children('[id]:even').addClass('odd');
};

ploneDnDReorder.doUp = function(e) {
    var dragging = ploneDnDReorder.dragging;
    if (!dragging) return;

    dragging.removeClass("dragging");
    ploneDnDReorder.updatePositionOnServer();
    dragging._position = null;
    try {
        delete dragging._position;
    } catch(e) {};
    dragging = null;
    ploneDnDReorder.rows.unbind('mousemove', ploneDnDReorder.doDrag);
    $(this).parents('tr').removeClass('dragindicator');
    return false;
};

ploneDnDReorder.updatePositionOnServer = function() {
    var dragging = ploneDnDReorder.dragging;
    if (!dragging) return;

    var delta = ploneDnDReorder.getPos(dragging) - dragging._position;

    if (delta == 0) {
        // nothing changed
        return;
    };
    // Strip off id prefix
    var args = {
        item_id: dragging.attr('id').substr('folder-contents-item-'.length)
    };
    args['delta:int'] = delta;
    jQuery.post('folder_moveitem', args)
};

})(jQuery);
