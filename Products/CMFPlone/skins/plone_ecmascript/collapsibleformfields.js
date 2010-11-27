/* This code collapses fields in forms
 * It uses the following markup:
 * 
 * <div class="collapsible'>
 *   <label class="collapser"> label of the field </label>
 *   <div class="collapse"> block to collapse </div>
 *  </div>
 * 
 */

(function($) {

$.fn.do_search_collapse = function() 
{
    return this.each(
	function() {
	    function check_used(element)
	    {
		e = $(element);
		
		// is there a number of checkboxs with a toggle box
		if (e.find('input[id$=_toggle]:checkbox').length > 0)
		{
		    // and the toggle checkbox is not checked.
		    if (e.find('input[id$=_toggle]:checkbox:checked').length == 0)
		    {
			return true;
		    }
		};

		// is there a normal text input fields that is not empty (=has a value) 
		if(e.find(':text[value]').length > 0){
		    return true;
		};
		
		// drop downs
		// we have an option marked as the default option
		if(e.find('select .default_option').length > 0)
		{
		    // and this default option isn't selected
		    if(e.find('select .default_option:selected').length == 0)
		    {
			return true;
		    }
		}
		return false;
	    };

            var indicator =  $(this).find('.collapser:first');
            var collapse = $(this).find('.collapse:first');
            indicator.click(function()
		{
		    var container = $(this).parent();
		    target = container.find('.collapse:first');
		    target.slideToggle('normal');
		    $(this).toggleClass('expanded');
		    $(this).toggleClass('collapsed');
		});
	    
	    if(check_used(this)){
		indicator.addClass('expanded');
	    } else {
		collapse.hide();
		indicator.addClass('collapsed');
	    };
	}
    );
};


})(jQuery);
