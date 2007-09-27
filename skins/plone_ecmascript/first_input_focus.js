// Focus on error or first element in a form with class="enableAutoFocus"
$(function() {
    if ($("form div.error :input:first").focus().length) return;
    $("form.enableAutoFocus :input:visible:first").focus();
});
