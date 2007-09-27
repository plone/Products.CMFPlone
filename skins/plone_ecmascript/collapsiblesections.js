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
 * This file uses functions from register_function.js
 *
 */

function toggleCollapsible(event) {
    var container = $(this).parents('dl.collapsible:eq(0)');
    if (!container) return true;

    if (container.hasClass('collapsedBlockCollapsible')) {
        container.removeClass('collapsedBlockCollapsible')
                 .addClass('expandedBlockCollapsible');
    } else if (container.hasClass('expandedBlockCollapsible')) {
        container.removeClass('expandedBlockCollapsible')
                 .addClass('collapsedBlockCollapsible');
    } else if (container.hasClass('collapsedInlineCollapsible')) {
        container.removeClass('collapsedInlineCollapsible')
                 .addClass('expandedInlineCollapsible');
    } else if (container.hasClass('expandedInlineCollapsible')) {
        container.removeClass('expandedInlineCollapsible')
                 .addClass('collapsedInlineCollapsible');
    }
};

function activateCollapsibles() {
    if (!W3CDOM) {return false;}

    $('dl.collapsible dt.collapsibleHeader:eq(0)').click(toggleCollapsible);
    $('dl.collapsible').each(function() {
        var state = $(this).hasClass('collapsedOnLoad') ?
                    'collapsed' : 'expanded';
        var type = $(this).hasClass('inline') ? 'Inline' :'Block';
        $(this).removeClass('collapsedOnLoad')
               .addClass(state + type + 'Collapsible');
    });
};

registerPloneFunction(activateCollapsibles);
