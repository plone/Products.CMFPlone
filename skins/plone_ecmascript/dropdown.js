
var actionMenuIds = new Array();

function getContainerWith(node, func) {
    // Starting with the given node, find the nearest containing element
    // for which the function func returns true.
    
    while (node != null) {
        if (func(node)) {
            return node;
        }
        node = node.parentNode;
    }
    return false;
}

function stringInList(name, list) {
    for (i = 0; i < list.length; i++) {
        if (list[i] == name){
            return true;
        }
    }
    return false;
}

function activateMenu(event) {
    if (!event) var event = window.event; // IE compatibility

    // terminate if we hit a non-compliant DOM implementation
    // returning true, so the link is still followed
    if (!document.getElementById){return true;}

    if (!this.className) {
        return true;
    }

    classes = this.className.split(' ');
    if (!stringInList('contentActionMenuHeader', classes)) {
        // not the correct element, the event needs to bubble up/down
        return true;
    }
    // last class is the menu_id
    menu_id = classes.pop();

    menu_body = document.getElementById(menu_id);
    if (!menu_body) {
        return true;
    }

    // check if the menu is visible
    if (menu_body.style.display && menu_body.style.display != 'none') {
        // it's visible - hide it
        menu_body.style.display = 'none';
    } else {
        // it's invisible - make it visible
        try {
            // using table fixes the cut off of elements in Firefox
            menu_body.style.display = 'table';
        } catch(e) {
            // IE doesn't know table
            menu_body.style.display = 'block';
        }
    }

    return false;
}

function isActionMenu(node) {
    if (node.className) {
        if (node.className.indexOf('actionMenu') >= 0) {
            return true;
        }
    }
    return false;
}

function menuDocumentMouseDown(event) {
    if (!event) var event = window.event; // IE compatibility

    if (event.target)
        targ = event.target;
    else if (event.srcElement)
        targ = event.srcElement;

    container = getContainerWith(targ, isActionMenu);
    if (container) {
        // targ is part of the menu, so just return and do the default
        return true;
    }

    // hide all menus
    for (i=0; i < actionMenuIds.length; i++) {
        menu_body = document.getElementById(actionMenuIds[i]);
        if (!menu_body) {
            continue
        }
        menu_body.style.display = 'none';
    }

    return true;
}

function menuMouseOver(event) {
    if (!event) var event = window.event; // IE compatibility

    if (!this.className) {
        return true;
    }

    classes = this.className.split(' ');
    if (!stringInList('contentActionMenuHeader', classes)) {
        // not the correct element, the event needs to bubble up/down
        return true;
    }
    // last class is the menu_id
    menu_id = classes.pop();

    var switch_menu = false;
    // hide all menus
    for (i=0; i < actionMenuIds.length; i++) {
        menu_body = document.getElementById(actionMenuIds[i]);
        if (!menu_body) {
            continue
        }
        // check if the menu is visible
        if (menu_body.style.display && menu_body.style.display != 'none') {
            switch_menu = true;
        }
        // turn off menu when it's not the current one
        if (menu_body.id != menu_id) {
            menu_body.style.display = 'none';
        }
    }

    if (switch_menu) {
        menu_body = document.getElementById(menu_id);
        try {
            // using table fixes the cut off of elements in Firefox
            menu_body.style.display = 'table';
        } catch(e) {
            // IE doesn't know table
            menu_body.style.display = 'block';
        }
    }

    return true;
}

function initializeMenus() {
    // terminate if we hit a non-compliant DOM implementation
    if (! document.getElementsByTagName){return false;}
    if (! document.getElementById){return false;}

    document.onmousedown = menuDocumentMouseDown

    links = document.getElementsByTagName('a');
    for (i=0; i < links.length; i++) {
        if (links[i].className.indexOf('contentActionMenuHeader')== -1) {
            continue
        }
        menu_header = links[i]

        // extract the target id
        classes = menu_header.className.split(' ')
        // last class is the menu_id
        menu_id = classes.pop();

        // see whether the target is available
        menu_body = document.getElementById(menu_id);
        if (!menu_body) {
            continue
        }

        actionMenuIds.push(menu_id);

        menu_header.onclick = activateMenu;
        menu_header.onmouseover = menuMouseOver;
    }
}

registerPloneFunction(initializeMenus);
