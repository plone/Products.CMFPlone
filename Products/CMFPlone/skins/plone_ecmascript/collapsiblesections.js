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

function activateCollapsibles() {
(function($) {
    $('dl.collapsible:not([class$=Collapsible])').find('dt.collapsibleHeader:first').click(function() {
        var $container = $(this).parents('dl.collapsible:first'),
            $type;
        if (!$container) {
            return true;
        }

        $type = $container.hasClass('inline') ? 'Inline' :'Block';
        // toggle between collapsed and expanded classes
        $container.toggleClass('collapsed' + $type + 'Collapsible')
                  .toggleClass('expanded' + $type + 'Collapsible');
    }).end().each(function() {
        var $state = $(this).hasClass('collapsedOnLoad') ?
                     'collapsed' : 'expanded',
            $type = $(this).hasClass('inline') ? 'Inline' :'Block';
        $(this).removeClass('collapsedOnLoad')
               .addClass($state + $type + 'Collapsible');
    });
}(jQuery));
}

jQuery(function($) {
$(activateCollapsibles);
});
