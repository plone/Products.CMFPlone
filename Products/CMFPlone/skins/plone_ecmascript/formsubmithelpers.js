function inputSubmitOnClick(event) {
    if (!event) var event = window.event; // IE compatibility

    if (hasClassName(this, 'submitting') && !hasClassName(this, 'allowMultiSubmit')) {
        return confirm(window.form_resubmit_message);
    } else {
        addClassName(this, 'submitting');
    }
    return true;
}

function registerSubmitHandler() {
    var nodes = cssQuery('input[type=submit]');
    for (var i=0; i<nodes.length; i++) {
        var node = nodes[i];
        if (!node.onclick) {
            node.onclick = inputSubmitOnClick;
        }
    }
}
registerPloneFunction(registerSubmitHandler);
