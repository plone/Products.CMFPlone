// Focus on error or first element in a form with class="enableAutoFocus"
function setFocus(){
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    var $elements = cssQuery("form div.error input,"+
                             "form div.error textarea,"+
                             "form div.error select");
    if ($elements.length > 0) {
        $elements[0].focus();
        return;
    }
    $elements = cssQuery("form.enableAutoFocus input[type=text],"+
                         "form.enableAutoFocus textarea");
    for (var i=0; i < $elements.length; i++) {
        if ($elements[i].type == 'hidden') {
            continue;
        }
        $elements[i].focus();
        break;
    }
}
if (typeof addDOMLoadEvent != "undefined") {
    addDOMLoadEvent(setFocus);
}
