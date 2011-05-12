/*
    Drag and drop reordering of folder contents.

    Provides global ploneDnDReorder
*/


/*jslint nomen:false */

var ploneDnDReorder = {};

ploneDnDReorder.dragging = null;
ploneDnDReorder.table = null;
ploneDnDReorder.rows = null;
ploneDnDReorder.locked = false;

(function($) {

ploneDnDReorder.doDown = function(e) {
    var dragging = ploneDnDReorder.dragging, 
        body;
    // Waiting for a server operation to complete or following an error
    if (ploneDnDReorder.locked) {return;}
    // already dragging, probably catching up a lost drag.
    if (dragging) {
        if ($(this).attr('id') !== dragging.attr('id')) {
            ploneDnDReorder.locked = true;
            dragging.removeClass('dragging').addClass('error');
        }
        return;
    }
    dragging =  $(this).parents('.draggable:first');
    if (!dragging.length) {return;}
    ploneDnDReorder.rows.mousemove(ploneDnDReorder.doDrag);
    body = $('body');
    body.mouseup(ploneDnDReorder.doUp);
    body.mouseleave(ploneDnDReorder.doCancel);

    ploneDnDReorder.dragging = dragging;
    dragging.data('ploneDnDReorder.startPosition', ploneDnDReorder.getPos(dragging));
    dragging.addClass("dragging");
    $(this).parents('tr').addClass('dragindicator');
    // Find the original subset ids. This must be in the current order.
    dragging.data('ploneDnDReorder.subset_ids', $.map(
        ploneDnDReorder.table.find('tr.draggable'),
        function(elem) {
            return $(elem).attr('id').substr('folder-contents-item-'.length);
    }));

    return false;
};

ploneDnDReorder.getPos = function(node) {
    var pos = node.parent().children('.draggable').index(node[0]);
    return pos === -1 ? null : pos;
};

ploneDnDReorder.doDrag = function(e) {
    var dragging = ploneDnDReorder.dragging,
        target = this;

    if (!dragging) {return;}
    if (!target) {return;}

    if ($(target).attr('id') !== dragging.attr('id')) {
        ploneDnDReorder.swapElements($(target), dragging);
    }
    return false;
};

ploneDnDReorder.swapElements = function(child1, child2) {
    var parent = child1.parent(),
        items = parent.children('[id]'),
        t;

    // Only adjacent elements may be swapped.
    if (Math.abs(ploneDnDReorder.getPos(child1) - ploneDnDReorder.getPos(child2)) !== 1) {
        return;
    }

    items.removeClass('even').removeClass('odd');
    if (child1[0].swapNode) {
        // IE proprietary method
        child1[0].swapNode(child2[0]);
    } else {
        // swap the two elements, using a textnode as a position marker
        t = parent[0].insertBefore(document.createTextNode(''),
                                       child1[0]);
        child1.insertBefore(child2);
        child2.insertBefore(t);
        $(t).remove();
    }
    // odd and even are 0-based, so we want them the other way around
    parent.children('[id]:odd').addClass('even');
    parent.children('[id]:even').addClass('odd');
};

ploneDnDReorder.doUp = function(e) {
    var dragging = ploneDnDReorder.dragging,
        body = $('body');
    if (!dragging) {return;}

    ploneDnDReorder.updatePositionOnServer();
    dragging.removeData('ploneDnDReorder.startPosition');
    dragging.removeData('ploneDnDReorder.subset_ids');
    ploneDnDReorder.rows.unbind('mousemove', ploneDnDReorder.doDrag);
    body.unbind('mouseup', ploneDnDReorder.doUp);
    body.unbind('mouseleave', ploneDnDReorder.doCancel);

    $(this).parents('tr').removeClass('dragindicator');
    return false;
};

ploneDnDReorder.doCancel = function(e) {
    var dragging = ploneDnDReorder.dragging,
        body = $('body');
    if (!dragging) {return;}

    dragging.removeClass("dragging")
    if (ploneDnDReorder.getPos(dragging) - dragging.data('ploneDnDReorder.startPosition')) {
        // position has changed, error out
        ploneDnDReorder.locked = true;
        dragging.addClass("error");
    }
    ploneDnDReorder.rows.unbind('mousemove', ploneDnDReorder.doDrag);
    body.unbind('mouseup', ploneDnDReorder.doCancel);
    body.unbind('mouseleave', ploneDnDReorder.doCancel);
    ploneDnDReorder.dragging = null;
    return false;
};

ploneDnDReorder.updatePositionOnServer = function() {
    var dragging = ploneDnDReorder.dragging,
        delta,
        args,
        encoded;

    if (!dragging) {return;}

    delta = ploneDnDReorder.getPos(dragging) - dragging.data('ploneDnDReorder.startPosition');

    if (delta === 0) {
        // nothing changed
        return;
    }
    // Strip off id prefix
    args = {
        item_id: dragging.attr('id').substr('folder-contents-item-'.length),
        subset_ids: dragging.data('ploneDnDReorder.subset_ids')
    };
    args['delta:int'] = delta;
    // Convert jQuery's name[]=1&name[]=2 to Zope's name:list=1&name:list=2
    encoded = $.param(args).replace(/%5B%5D=/g, '%3Alist=');
    $.ajax({
        type: 'POST',
        url: 'folder_moveitem',
        data: encoded,
        complete: ploneDnDReorder.complete
    });
    ploneDnDReorder.locked = true;
};

ploneDnDReorder.complete = function(xhr, textStatus) {
    var dragging = ploneDnDReorder.dragging;
    dragging.removeClass("dragging");
    if (textStatus === "success" || textStatus === "notmodified") {
        ploneDnDReorder.locked = false;
    } else {
        dragging.addClass("error");
    }
    ploneDnDReorder.dragging = null;
};


}(jQuery));
