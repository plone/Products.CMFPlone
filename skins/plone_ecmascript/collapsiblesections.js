/*
 * This is the code for the collapsibles. It uses the following markup:
 *
 * <dl class="collapsible">
 *   <dt class="collapsibleHeader">
 *     A Title
 *   </dt>
 *   <dd class="collapsibleContent">
 *     <!-- Here can be any content you want -->
 *   </dd>
 * </dl>
 *
 * When the collapsible is toggled, then the dl will get an additional class
 * which switches between 'collapsed' and 'expanded'.
 * You can use this to style it accordingly, for example:
 *
 * .collapsible.expanded .collapsibleContent {
 *   display: block;
 * }
 *
 * .collapsible.collapsed .collapsibleContent {
 *   display: none;
 * }
 *
 * If you add the 'collapsedOnLoad' class to the dl, then it will get
 * collapsed on page load, this is done, so the content is accessible even when
 * javascript is disabled.
 *
 * This file uses functions from register_function.js, cssQuery.js and
 * nodeutils.js.
 *
 */

function isCollapsible(node) {
    if (hasClassName(node, 'collapsible')) {
        return true;
    }
    return false;
};

function toggleCollapsible(event) {
    if (!event) var event = window.event; // IE compatibility

    if (!this.tagName && (this.tagName == 'DT' || this.tagName == 'dt')) {
        return true;
    }

    var container = findContainer(this, isCollapsible);
    if (!container) {
        return true;
    }

    if (hasClassName(container, 'collapsed')) {
        replaceClassName(container, 'collapsed', 'expanded');
    } else if (hasClassName(container, 'expanded')) {
        replaceClassName(container, 'expanded', 'collapsed');
    }
};

function activateCollapsibles() {
    if (!W3CDOM) {return false;}

    var collapsibles = cssQuery('dl.collapsible');
    for (var i in collapsibles) {
        collapsible = collapsibles[i];

        var collapsible_header = cssQuery('dt.collapsibleHeader', collapsible)[0];
        collapsible_header.onclick = toggleCollapsible;

        if (hasClassName(collapsible, 'collapsedOnLoad')) {
            replaceClassName(collapsible, 'collapsedOnLoad', 'collapsed');
        } else {
            addClassName(collapsible, 'expanded');
        }
    }
};

registerPloneFunction(activateCollapsibles);
