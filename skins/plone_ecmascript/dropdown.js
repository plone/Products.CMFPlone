
var actionMenus = new Array();
var actionMenuIds = new Array();

function activateMenu(event) {
    if (!event) var event = window.event; // IE compatibility

    class_name = this.className;
    if (class_name.indexOf('contentActionMenuHeader')== -1) {
        // not the correct element, the event needs to bubble up/down
        return true;
    }
    // extract the target id
    classes = class_name.split(' ');
    // last class is the menu_id
    menu_id = classes.pop();

    if (!actionMenus[menu_id]) {
        return true;
    }
    menu = actionMenus[menu_id];
    menu_body = menu.body;

    if (menu_body.style.display != 'none') {
        menu_body.style.display = 'none';
    } else {
        try {
            // using table fixes the cut off of elements in Firefox
            menu_body.style.display = 'table';
        } catch(e) {
            // IE doesn't know table
            menu_body.style.display = 'block';
        }
        menu.active = true;
    }

    return false;
}

function menuDocumentMouseDown(event) {
    if (!event) var event = window.event; // IE compatibility

    // hide all menus
    for (i=0; i < actionMenuIds.length; i++) {
        menu = actionMenus[actionMenuIds[i]]
        if (!menu) {
            continue
        }
        menu.body.style.display = 'none';
        menu.active = false;
    }

    return false;
}

function menuMouseOver(event) {
    if (!event) var event = window.event; // IE compatibility

    class_name = this.className;
    if (class_name.indexOf('contentActionMenuHeader')== -1) {
        // not the correct element, the event needs to bubble up/down
        return true;
    }
    // extract the target id
    classes = class_name.split(' ');
    // last class is the menu_id
    menu_id = classes.pop();

    var switch_menu = false;
    // hide all menus
    for (i=0; i < actionMenuIds.length; i++) {
        menu = actionMenus[actionMenuIds[i]]
        if (!menu) {
            continue
        }
        if (menu.active) {
            // we have to turn on another menu below
            switch_menu = true;
        }
        if (menu.id != menu_id) {
            // turn off menu when it's not the current one
            menu.body.style.display = 'none';
        }
    }

    if (switch_menu) {
        menu_body = actionMenus[menu_id].body;
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
    // returning true, so the link is still followed
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

        if (!actionMenus[menu_id]) {
            menu = new Object();
            actionMenus[menu_id] = menu;
            actionMenuIds.push(menu_id);
        } else {
            menu = actionMenus[menu_id];
        }
        menu.id = menu_id;
        menu.active = false;
        menu.header = menu_header;
        menu.body = menu_body;

        menu_header.onclick = activateMenu;
        menu_header.onmouseover = menuMouseOver;
    }
}

registerPloneFunction(initializeMenus);
