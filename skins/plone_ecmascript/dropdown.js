/*
 * This is the code for the dropdown menus. It uses the following markup:
 *
 * <dl class="actionMenu" id="uniqueIdForThisMenu">
 *   <dt class="actionMenuHeader">
 *     <!-- The following a-tag needs to be clicked to dropdown the menu -->
 *     <a href="some_destination">A Title</a>
 *   </dt>
 *   <dd class="actionMenuContent">
 *     <!-- Here can be any content you want -->
 *   </dd>
 * </dl>
 *
 * When the menu is toggled, then the dl with the class actionMenu will get an
 * additional class which switches between 'activated' and 'deactivated'.
 * You can use this to style it accordingly, for example:
 *
 * .actionMenu.activated {
 *   display: block;
 * }
 *
 * .actionMenu.deactivated {
 *   display: none;
 * }
 *
 * When you click somewhere else than the menu, then all open menus will be
 * deactivated. When you move your mouse over the a-tag of another menu, then
 * that one will be activated and all others deactivated.
 *
 * This file uses functions from register_function.js, cssQuery.js and
 * nodeutils.js.
 *
 */

function isActionMenu(node) {
    if (hasClassName(node, 'actionMenu')) {
        return true;
    }
    return false;
};

function toggleMenu(event) {
    if (!event) var event = window.event; // IE compatibility

    // terminate if we hit a non-compliant DOM implementation
    // returning true, so the link is still followed
    if (!W3CDOM){return true;}

    if (!this.tagName && (this.tagName == 'A' || this.tagName == 'a')) {
        return true;
    }

    var container = findContainer(this, isActionMenu);
    if (!container) {
        return true;
    }

    // check if the menu is visible
    if (hasClassName(container, 'activated')) {
        // it's visible - hide it
        replaceClassName(container, 'activated', 'deactivated', true);
    } else {
        // it's invisible - make it visible
        replaceClassName(container, 'deactivated', 'activated', true);
    }

    return false;
};

function actionMenuDocumentMouseDown(event) {
    if (!event) var event = window.event; // IE compatibility

    if (event.target)
        targ = event.target;
    else if (event.srcElement)
        targ = event.srcElement;

    var container = findContainer(targ, isActionMenu);
    if (container) {
        // targ is part of the menu, so just return and do the default
        return true;
    }

    // hide all menus
    menus = cssQuery('dl.actionMenu');
    for (var i in menus) {
        replaceClassName(menus[i], 'activated', 'deactivated', true);
    }

    return true;
};

function actionMenuMouseOver(event) {
    if (!event) var event = window.event; // IE compatibility

    if (!this.tagName && (this.tagName == 'A' || this.tagName == 'a')) {
        return true;
    }

    var container = findContainer(this, isActionMenu);
    if (!container) {
        return true;
    }
    var menu_id = container.id;

    var switch_menu = false;
    // hide all menus
    var menus = cssQuery('dl.actionMenu');
    for (var i in menus) {
        var menu = menus[i]
        // check if the menu is visible
        if (hasClassName(menu, 'activated')) {
            switch_menu = true;
        }
        // turn off menu when it's not the current one
        if (menu.id != menu_id) {
            replaceClassName(menu, 'activated', 'deactivated', true);
        }
    }

    if (switch_menu) {
        var menu = cssQuery('#'+menu_id)[0];
        if (menu) {
            replaceClassName(menu, 'deactivated', 'activated', true);
        }
    }

    return true;
};

function initializeMenus() {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM) {return false;}

    document.onmousedown = actionMenuDocumentMouseDown;

    // hide all menus
    menus = cssQuery('dl.actionMenu');
    for (var i in menus) {
        replaceClassName(menus[i], 'activated', 'deactivated', true);
    }

    var menu_headers = cssQuery('dl.actionMenu > dt.actionMenuHeader > a');
    for (var i in menu_headers) {
        menu_header = menu_headers[i];

        menu_header.onclick = toggleMenu;
        menu_header.onmouseover = actionMenuMouseOver;
    }
};

registerPloneFunction(initializeMenus);
