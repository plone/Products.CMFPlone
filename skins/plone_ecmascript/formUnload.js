/* BeforeUnload form processing */
if (!window.beforeunload) (function() {
    var BeforeUnloadHandler = function() {
        var self = this;

        this.message = window.form_modified_message ||
            "Discard changes? If you click OK, any changes you have made will be lost.";

        this.forms = [];
        this.chkId = [];
        this.chkType = new this.CheckType();
        this.handlers = [this.isAnyFormChanged];
        this.submitting = false;

        this.execute = function(event) {
            // First clean out dead references to make sure we only work on
            // forms that are actually in the dom. This is needed in
            // combination with KSS and/or other dynamic replacements.
            var domforms = document.getElementsByTagName('form'); 
            var forms_in_dom = [];
            for(var i=0; i<self.forms.length; i++){
                for(var j=0; j<domforms.length; j++){
                    if(self.forms[i]==domforms[j]){
                        forms_in_dom.push(domforms[j]);
                    }
                }
            }
            self.forms = forms_in_dom;
             
            
            // Now do the protection work
            if (self.submitting) return;
            if (!event) event = window.event;

            for (var i = 0; i < self.handlers.length; i++) {
                var fn = self.handlers[i];
                var message = message || fn.apply(self);
            }
            if (message===true) message = self.message;
            if (message===false) message = undefined;
            if (event && message) { event.returnValue = message; }
            return message;
        }
        this.execute.tool = this;
    }
    var Class = BeforeUnloadHandler.prototype;

    // form checking code
    Class.isAnyFormChanged = function() {
        for (var i=0; i < this.forms.length; i++) {
            var form = this.forms[i];
            if (this.isElementChanged(form)) {
                return true;
            }
        }
        return false;
    }
    Class.addHandler = function(fn) {
        this.handlers.push(fn);
    }
    Class.onsubmit = function() {
        var tool = window.onbeforeunload && window.onbeforeunload.tool;
        tool.submitting = true;
        // Also set this on the unlocking tool!
        // This way the tool knows we are in submitting,
        // and can prevent unlocking.
        var lockingtool = window.onunload && window.onunload.tool;
        lockingtool.submitting = true;
    }
    Class.addForm = function(form) {
        for (var i = 0; i < this.forms.length; i++) {
            if (this.forms[i]==form) return;
        }
        this.forms.push(form);
        form.onsubmit = this.onsubmit;
        var elements = form.getElementsByTagName('input');
        for (var j = 0; j < elements.length; j++) {
            var ele = elements[j];
            if (ele.type=='hidden') {
                ele.setAttribute('originalValue', ele.defaultValue);
            }
        }
    }
    Class.addForms = function() {
        for (var i = 0; i < arguments.length; i++) {
            var element = arguments[i];
            if (!element) continue;
            if (element.tagName=='FORM') {
                this.addForm(element);
            }
            else {
                var forms = element.getElementsByTagName('form');
                for (var j = 0; j < forms.length; j++) {
                    this.addForm(forms[j]);
                }
            }
        }
    }
    Class.removeForms = function() {
        for (var i = 0; i < arguments.length; i++) {
            var element = arguments[i];
            if (!element) continue;
            if (element.tagName=='FORM') {
                for (var j = 0; j < arguments.length; j++) {
                    if (this.forms[j] == element) {
                        this.forms.splice(j--, 1);
                        element.onsubmit=null;
                    }
                }
            } else {
                var forms = element.getElementsByTagName('form');
                for (var j = 0; j < forms.length; j++) {
                    this.removeForms(forms[j]);
                }
            }
        }
    }

    Class.CheckType = function() {};
    var c = Class.CheckType.prototype;
    c.checkbox = c.radio = function(ele) {
        return ele.checked != ele.defaultChecked;
    }
    c.password = c.textarea = c.text = function(ele) {
        return ele.value != ele.defaultValue;
    }
    // hidden: cannot tell on Mozilla without special treatment
    c.hidden = function(ele) {
        var orig = ele.getAttribute("originalValue");
        return orig && (ele.value != orig);
    }

    c['select-one'] = function(ele) {
        for (var i=0 ; i < ele.length; i++) {
            var opt = ele.options[i];
            if ( opt.selected != opt.defaultSelected) {
                if (i===0 && opt.selected) continue; /* maybe no default */
                return true;
            }
        }
        return false;
    }

    c['select-multiple'] = function(ele) {
        for (var i=0 ; i < ele.length; i++) {
            var opt = ele.options[i];
            if ( opt.selected != opt.defaultSelected) {
                return true;
            }
        }
        return false;
    }

    Class.chk_form = function(form) {
        var elements = form.elements;
        for (var i=0; i < elements.length; i++ ) {
            var element = elements[i];
            if (this.isElementChanged(element)) {
                return true;
            }
        }
        return false;
    }

    Class.isElementChanged = function(ele) {
        var method = ele.id && this.chkId[ele.id];
        if (!method && ele.type && ele.name)
            method = this.chkType[ele.type];
        if (!method && ele.tagName)
            method = this['chk_'+ele.tagName.toLowerCase()];

        return method? method.apply(this, [ele]) : false;
    };

    window.onbeforeunload = new BeforeUnloadHandler().execute;
    
    registerPloneFunction(function() {
        // terminate if we hit a non-compliant DOM implementation
        if (!W3CDOM){return false};

        var tool = window.onbeforeunload && window.onbeforeunload.tool;
        var content = getContentArea();
        if (tool && content) {
            var forms = cssQuery('form.enableUnloadProtection');
            for (var i=0; i < forms.length; i++) {
                tool.addForm(forms[i]);
            }
        }
    });
})();
