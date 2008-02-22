function inputSubmitOnClick(event) {
    if (jq(this).hasClass('submitting') && !jq(this).hasClass('allowMultiSubmit'))
        return confirm(window.form_resubmit_message);
    else
        jq(this).addClass('submitting');
}

jq(function() {
    jq(':submit').each(function() {
      if (!this.onclick)
        jq(this).click(inputSubmitOnClick);
    });
});
