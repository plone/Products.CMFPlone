/* This code collapses fields in forms
 * It is used in plone_forms/search_form.pt
 *
 * Creates a jQuery function to install a click handler that will
 * collapse/expand form fields.
 * On page load, runs it for $('.field.collapsible').
 *
 * It uses the following markup:
 *
 * <div class="collapsible'>
 *   <label class="collapser"> label of the field </label>
 *   <div class="collapse"> block to collapse </div>
 *  </div>
 *
 */


(function($) {

$.fn.do_search_collapse = function() {

    function check_used(element) {
        var e = $(element);

        // is there a number of checkboxs with a toggle box
        if (e.find('input[id$=_toggle]:checkbox').length > 0) {
            // and the toggle checkbox is not checked.
            if (e.find('input[id$=_toggle]:checkbox:checked').length === 0) {
                return true;
            }
        }

        // is there a normal text input fields that is not empty (=has a value)
        if(e.find(':text[value]').length > 0) {
            return true;
        }

        // drop downs
        // we have an option marked as the default option
        if(e.find('select .default_option').length > 0) {
            // and this default option isn't selected
            if(e.find('select .default_option:selected').length === 0) {
                return true;
            }
        }
        return false;
    }

    return this.each( function() {
        var indicator =  $(this).find('.collapser:first'),
            collapse = $(this).find('.collapse:first');

        // install click handler
        indicator.click(function() {
                var container = $(this).parent(),
                    target = container.find('.collapse:first');

                target.slideToggle('normal');
                $(this).toggleClass('expanded');
                $(this).toggleClass('collapsed');
            });

        if (check_used(this)) {
            indicator.addClass('expanded');
        } else {
            collapse.hide();
            indicator.addClass('collapsed');
        }
    });
};

jQuery(function($){$('.field.collapsible').do_search_collapse();});


}(jQuery));
