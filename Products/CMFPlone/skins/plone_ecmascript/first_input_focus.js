// Focus on error or first element in a form with class="enableAutoFocus"

jQuery(function($) {
    if ($("form div.error :input:first").focus().length) {return;}
    $("form.enableAutoFocus :input:not(.formTabs):visible:first").focus();
});
