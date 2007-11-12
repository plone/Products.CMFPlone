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
 * which switches between 'collapsedBlockCollapsible' and
 * 'expandedBlockCollapsible'. You can use this to style it accordingly, for
 * example:
 *
 * .expandedBlockCollapsible .collapsibleContent {
 *   display: block;
 * }
 *
 * .collapsedBlockCollapsible .collapsibleContent {
 *   display: none;
 * }
 *
 * If you add the 'collapsedOnLoad' class to the dl, then it will get
 * collapsed on page load, this is done, so the content is accessible even when
 * javascript is disabled.
 *
 * If you add the 'inline' class to the dl, then it will toggle between
 * 'collapsedInlineCollapsible' and 'expandedInlineCollapsible' instead of
 * 'collapsedBlockCollapsible' and 'expandedBlockCollapsible'.
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

    if (hasClassName(container, 'collapsedBlockCollapsible')) {
        replaceClassName(container, 'collapsedBlockCollapsible', 'expandedBlockCollapsible');
    } else if (hasClassName(container, 'expandedBlockCollapsible')) {
        replaceClassName(container, 'expandedBlockCollapsible', 'collapsedBlockCollapsible');
    } else if (hasClassName(container, 'collapsedInlineCollapsible')) {
        replaceClassName(container, 'collapsedInlineCollapsible', 'expandedInlineCollapsible');
    } else if (hasClassName(container, 'expandedInlineCollapsible')) {
        replaceClassName(container, 'expandedInlineCollapsible', 'collapsedInlineCollapsible');
    }
};

function activateCollapsibles() {
    if (!W3CDOM) {return false;}

    var collapsibles = cssQuery('dl.collapsible');
    for (var i=0; i < collapsibles.length; i++) {
        var collapsible = collapsibles[i];

        var collapsible_header = cssQuery('dt.collapsibleHeader', collapsible)[0];
        collapsible_header.onclick = toggleCollapsible;

        if (hasClassName(collapsible, 'inline')) {
            // the collapsible should be inline
            if (hasClassName(collapsible, 'collapsedOnLoad')) {
                replaceClassName(collapsible, 'collapsedOnLoad', 'collapsedInlineCollapsible');
            } else {
                addClassName(collapsible, 'expandedInlineCollapsible');
            }
        } else {
            // the collapsible is a block
            if (hasClassName(collapsible, 'collapsedOnLoad')) {
                replaceClassName(collapsible, 'collapsedOnLoad', 'collapsedBlockCollapsible');
            } else {
                addClassName(collapsible, 'expandedBlockCollapsible');
            }
        }
    }
};

registerPloneFunction(activateCollapsibles);
