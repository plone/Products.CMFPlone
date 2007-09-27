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
 */

function toggleCollapsible(event) {
    var container = $(this).parents('dl.collapsible:first');
    if (!container) return true;

    var type = container.hasClass('inline') ? 'Inline' :'Block';
    if (container.hasClass('collapsed' + type + 'Collapsible')) {
        container.removeClass('collapsed' + type + 'Collapsible')
                 .addClass('expanded' + type + 'Collapsible');
    } else if (container.hasClass('expanded' + type + 'Collapsible')) {
        container.removeClass('expanded' + type + 'Collapsible')
                 .addClass('collapsed' + type + 'Collapsible');
    }
};

$(function() {
    $('dl.collapsible dt.collapsibleHeader:first').click(toggleCollapsible);
    $('dl.collapsible').each(function() {
        var state = $(this).hasClass('collapsedOnLoad') ?
                    'collapsed' : 'expanded';
        var type = $(this).hasClass('inline') ? 'Inline' :'Block';
        $(this).removeClass('collapsedOnLoad')
               .addClass(state + type + 'Collapsible');
    });
});