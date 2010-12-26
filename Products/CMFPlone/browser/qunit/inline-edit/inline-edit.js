

/* XXX This should either become a resource, or moved over to skins,
 * and in the latter case be referenced differently from the demo.html and test.html */

/* Based on code of Eric Steele */

(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

/* this should only happen from the pages */
/* 
$(function(){
    $(window).addInlineEditing();
});
*/

/* Widget class */

var KssBaseWidget = function() {};
$.extend(KssBaseWidget.prototype, {

    init: function(base_href){
        this.base_href = base_href;
    },

    getKSSAttr: function(obj, varname){
        classes = obj.attr('class').split(' ');
        classname = 'kssattr-' + varname + '-';
        for (i in classes){
            cls = classes[i];
            if(cls.indexOf(classname) >= 0){
                return cls.substring(classname.length, cls.length);
            }
        }
        
        inherited = obj.parents("[class*='" + classname + "']");
        if (inherited.length){
            return getKSSAttr(inherited, varname);
        }

        return '';
    },

    handleKSSResponse: function(response){
        $(response).find('command').each(function(){
                doKSSCommand(this);
        });
    },

    extractSelector: function(command){
        selector = $(command).attr('selector');
        selectorType = $(command).attr('selectorType');
        switch (selectorType){
            case 'htmlid':
                return '#' + selector;
            case 'css':
                return selector;
            default:
                return selector;
        }
    },

    doKSSCommand: function(command){
        selector = extractSelector(command);
        commandName = $(command).attr('name');
        switch (commandName){
            case 'clearChildNodes':
                $(selector).empty();
                break;
            case 'focus':
                $(selector).focus();
                break;            
            case 'replaceHTML':
                html = $(command).find('param[name="html"]').text();
                $(selector).replaceWith(html);
                break;
            case 'replaceInnerHTML':
                html = $(command).find('param[name="html"]').text();
                $(selector).html(html);
                break;
            case 'setAttribute':
                attributeName = $(command).find('param[name="name"]').text();
                replaceText = $(command).find('param[name="value"]').text();
                $(selector).attr(attributeName, replaceText);   
                break;
            case 'setStyle':
                name = $(command).find('param[name="name"]').text();
                value = $(command).find('param[name="value"]').text();
                $(selector).css(name, value);
                break;
            default:
                if (console) {
                    console.log('No handler for command ' + $(command).attr('name'));
                }
        }
    },


});

var InlineEditing = function() {};

$.extend(InlineEditing.prototype, KssBaseWidget.prototype, {

    bind: function(options){
        var self = this;
        this.init(options.base_href);

        log('base_href', this.base_href, options);

        $(document).data('InlineEditing', this);

        $('.inlineEditable').live('click', function(){
            log('CLICK!');
            serviceURL = self.base_href + '@@replaceField';
            params = {
                'fieldname': self.getKSSAttr($(this), 'atfieldname'),
                'templateId': self.getKSSAttr($(this), 'templateId'),
                'macro': self.getKSSAttr($(this), 'macro'),
                'edit': 'True'
            };
            uid = self.getKSSAttr($(this), 'atuid');
            if (uid){
                params['uid']=uid;
            }
            target = self.getKSSAttr($(this), 'target');
            if (target){
                params['target']=target;
            }
            log('get...');
            $.get(serviceURL, params, function(data){
                log('response...');
                self.handleKSSResponse(data);
            });
            log('get over.');
        });

        $('form.inlineForm input[name="kss-save"]').live('click', function(){
            serviceURL = self.base_href + '@@saveField';
            fieldname = self.getKSSAttr($(this), 'atfieldname');
            params = {
                'fieldname': fieldname
            };
        
            valueSelector = "input[name='" + params['fieldname'] + "']";
            value = $(this).parents('form').find(valueSelector).val();
            if (value){
                params['value']={
                    fieldname: value
                }
            }
        
            templateId = self.getKSSAttr($(this), 'templateId');
            if (templateId){
                params['templateId']=templateId;
            }
        
            macro = self.getKSSAttr($(this), 'macro');
            if (macro){
                params['macro']=macro;
            }
        
            uid = self.getKSSAttr($(this), 'atuid');
            if (uid){
                params['uid']=uid;
            }
        
            target = self.getKSSAttr($(this), 'target');
            if (target){
                params['target']=target;
            }

            $.get(serviceURL, params, function(data){
                self.handleKSSResponse(data);
            });        
        });
       
        $('form.inlineForm input[name="kss-cancel"]').live('click', function(){
            self.cancelInlineEdit(this);
        });
        
        $('input.blurrable, select.blurrable, textarea.blurrable').live('keypress', function(event){
            if (event.keyCode == 27){
                self.cancelInlineEdit(this);
            }
        });
    },

    unbind: function(options){
        var self = this;

        $('.inlineEditable').die('click');
        $('form.inlineForm input[name="kss-save"]').die('click');
        $('form.inlineForm input[name="kss-cancel"]').die('click');
        $('input.blurrable, select.blurrable, textarea.blurrable').die('keypress');

        $(document).removeData('InlineEditing');
    },

    cancelInlineEdit: function(obj){
        var self = this;

        serviceURL = this.base_href + '@@replaceWithView';
        fieldname = this.getKSSAttr($(obj), 'atfieldname');
        params = {'fieldname': fieldname,
                  'edit':      true};
        templateId = this.getKSSAttr($(obj), 'templateId');
        if (templateId){
            params['templateId']=templateId;
        }

        macro = this.getKSSAttr($(obj), 'macro');
        if (macro){
            params['macro']=macro;
        }

        uid = this.getKSSAttr($(obj), 'atuid');
        if (uid){
            params['uid']=uid;
        }

        target = this.getKSSAttr($(obj), 'target');
        if (target){
            params['target']=target;
        }
        $.get(serviceURL, params, function(data){self.handleKSSResponse(data);});
    }

});

/* register a jQuery plugin */
jQuery.fn.extend({

    addInlineEditing: function(base_href) {

        if (this.length != 1) {
            throw Error('allowInlineEditing needs to be bound to exactly one element: the window or the document.');
        }
        var node = this[0];
        if (node !== window && node !== document) {
            throw Error('allowInlineEditing needs to be bound to the window or the document.');
        }
        if ($(document).data('InlineEditing')) {
            throw Error('allowInlineEditing is already bound, cannot bind it again.');
        }

        var inlineEditing = new InlineEditing();
        inlineEditing.bind({
            base_href: base_href
        });
    },

    removeInlineEditing: function() {
        /* Inline Editing */

        var inlineEditing = $(document).data('InlineEditing');
        if (inlineEditing) {
            inlineEditing.unbind();
        }
    }


});


})(jQuery);

