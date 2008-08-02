// Focus on error or first element in a form with class="enableAutoFocus"
jq(function() {
    if (jq("form div.error :input:first").focus().length) return;
    jq("form.enableAutoFocus :input:not(.formTabs):visible:first").focus();
});
