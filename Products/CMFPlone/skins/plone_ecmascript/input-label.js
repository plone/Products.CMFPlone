/* This looks for input fields with a title and the class "inputLabel". When
   the field is empty the title will be set as it's value and the class
   "inputLabel" will be replaced with the class "inputLabelActive" to make
   it styleable with css. When the field gets focus, the content is removed
   and the class "inputLabelActive" is removed. When the field looses focus,
   then the game starts again if the value is empty, if not then the field
   is left as is. When the form is submitted, the values are cleaned up
   before they are sent to the server. If there already is a submit function,
   then it will be called afterwards.
*/

var ploneInputLabel = {
    focus: function() {
        return function(e) {
            var target;
            if (!e) var e = window.event;
            if (e.target) target = e.target;
            else if (e.srcElement) target = e.srcElement;
            if (target.nodeType == 3) // defeat Safari bug
                target = target.parentNode;
            if (hasClassName(target, "inputLabelActive") && (target.value == target.title)) {
                target.value = '';
                removeClassName(target, "inputLabelActive");
            }
        }
    },

    blur: function() {
        return function(e) {
            var target;
            if (!e) var e = window.event;
            if (e.target) target = e.target;
            else if (e.srcElement) target = e.srcElement;
            if (target.nodeType == 3) // defeat Safari bug
                target = target.parentNode;
            if (target.value == '') {
                addClassName(target, "inputLabelActive");
                target.value = target.title;
            }
        }
    },

    isForm: function(node) {
        return (node.tagName && node.tagName.toLowerCase() == 'form')
    },

    submit: function() {
        return function(e) {
            var target;

            if (!e) var e = window.event;
            if (e.target) target = e.target;
            else if (e.srcElement) target = e.srcElement;
            if (target.nodeType == 3) // defeat Safari bug
                target = target.parentNode;

            var elements = cssQuery("input[title].inputLabelActive");

            for (var i=0; i<elements.length; i++) {
                var element = elements[i];
                if (hasClassName(element, "inputLabelActive") && (element.value == element.title)) {
                    element.value = '';
                    removeClassName(element, "inputLabelActive");
                }
            }
            if (target.inputLabelData.oldsubmit)
                return this.inputLabelData.oldsubmit();
        }
    },

    init: function() {
        // look for input elements with a title and inputLabel class
        var elements = cssQuery("input[title].inputLabel");
        for (var i=0; i<elements.length; i++) {
            var element = elements[i];
            var form = findContainer(element, ploneInputLabel.isForm);

            if (element.value == '') {
                element.value = element.title;
                replaceClassName(element, "inputLabel", "inputLabelActive");
            }
            registerEventListener(element, 'focus', ploneInputLabel.focus());
            registerEventListener(element, 'blur', ploneInputLabel.blur());
            if (form.onsubmit != ploneInputLabel.submit) {
                if (typeof form.inputLabelData == 'undefined')
                    form.inputLabelData = new Object();
                form.inputLabelData.oldsubmit = form.onsubmit;
                form.onsubmit = ploneInputLabel.submit();
            }
        }
    }
};

registerPloneFunction(ploneInputLabel.init);
