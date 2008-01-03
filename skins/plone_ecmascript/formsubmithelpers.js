function inputSubmitOnClick(event) {
    if ($(this).hasClass('submitting') && !$(this).hasClass('allowMultiSubmit'))
        return confirm(window.form_resubmit_message);
    else
        $(this).addClass('submitting');
}

$(function() {
    $(':submit').each(function() {
      if (!this.onclick)
        $(this).click(inputSubmitOnClick);
    });
});
