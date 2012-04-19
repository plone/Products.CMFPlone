function inputSubmitOnClick(event) {
    if (jQuery(this).hasClass('submitting') && !jQuery(this).hasClass('allowMultiSubmit'))
        return confirm(window.form_resubmit_message);
    else
        jQuery(this).addClass('submitting');
}

(function($) { $(function() {
    $('input:submit').each(function() {
      if (!this.onclick)
        $(this).click(inputSubmitOnClick);
    });
}); })(jQuery);
