/*
 * This is the code for the tabbed forms. It assumes the following markup:
 *
 * <form class="enableFormTabbing">
 *   <fieldset id="fieldset-[unique-id]">
 *     <legend id="fieldsetlegend-[same-id-as-above]">Title</legend>
 *   </fieldset>
 * </form>
 *
 * or the following
 *
 * <dl class="enableFormTabbing">
 *   <dt id="fieldsetlegend-[unique-id]">Title</dt>
 *   <dd id="fieldset-[same-id-as-above]">
 *   </dd>
 * </dl>
 *
 */


var ploneFormTabbing = {
        // standard jQueryTools configuration options for all form tabs
        jqtConfig:{current:'selected'}
    };


(function($) {

ploneFormTabbing._buildTabs = function(container, legends) {
    var threshold = legends.length > 6;
    var panel_ids, tab_ids = [], tabs = '';

    for (var i=0; i < legends.length; i++) {
        var className, tab, legend = legends[i], lid = legend.id;
        tab_ids[i] = '#' + lid;

        switch (i) {
            case (0):
                className = 'class="formTab firstFormTab"';
                break;
            case (legends.length-1):
                className = 'class="formTab lastFormTab"';
                break;
            default:
                className = 'class="formTab"';
                break;
        }

        if (threshold) {
            tab = '<option '+className+' id="'+lid+'" value="'+lid+'">';
            tab += $(legend).text()+'</option>';
        } else {
            tab = '<li '+className+'><a id="'+lid+'" href="#'+lid+'"><span>';
            tab += $(legend).text()+'</span></a></li>';
        }

        tabs += tab;
        $(legend).hide();
    }

    tab_ids = tab_ids.join(',');
    panel_ids = tab_ids.replace(/#fieldsetlegend-/g, "#fieldset-");

    if (threshold) {
        tabs = $('<select class="formTabs">'+tabs+'</select>');
        tabs.change(function(){
        	var selected = $(this).attr('value');
        	jq('#'+selected).click();
        })
    } else {
        tabs = $('<ul class="formTabs">'+tabs+'</ul>');
    }

    return tabs;
};


ploneFormTabbing.initializeDL = function() {
    var ftabs = $(ploneFormTabbing._buildTabs(this, $(this).children('dt')));
    var targets = $(this).children('dd');
    $(this).before(ftabs);
    targets.addClass('formPanel');
    ftabs.tabs(targets, ploneFormTabbing.jqtConfig);
};


ploneFormTabbing.initializeForm = function() {
    var jqForm = $(this);
    var fieldsets = jqForm.children('fieldset');

    if (!fieldsets.length) {return;}

    var ftabs = ploneFormTabbing._buildTabs(
        this, fieldsets.children('legend'));
    $(this).prepend(ftabs);
    fieldsets.addClass("formPanel");


    // The fieldset.current hidden may change, but is not content
    $(this).find('input[name="fieldset.current"]').addClass('noUnloadProtection');

    $(this).find('.formPanel:has(div.field span.required)').each(function() {
        var id = this.id.replace(/^fieldset-/, "#fieldsetlegend-");
        $(id).addClass('required');
    });

    // set the initial tab
    var initialIndex = 0;
    var count = 0;
    var found = false;
    $(this).find('.formPanel').each(function() {
        if (!found && $(this).find('div.field.error').length!=0) {
            initialIndex = count;
            found = true;
        }
        count += 1;
    });

    var tabSelector = 'ul.formTabs';
    if ($(ftabs).is('select.formTabs')) {
        tabSelector = 'select.formTabs';
    }
    var tabsConfig = $.extend({}, ploneFormTabbing.jqtConfig, {'initialIndex':initialIndex});
    jqForm.children(tabSelector).tabs(
        'form.enableFormTabbing fieldset.formPanel',
        tabsConfig
        );

    // save selected tab on submit
    jqForm.submit(function() {
    	var selected;
    	if(ftabs.find('a.selected').length>=1){
    		selected = ftabs.find('a.selected').attr('href').replace(/^#fieldsetlegend-/, "#fieldset-");
    	}
    	else{
    		selected = ftabs.attr('value').replace(/^fieldsetlegend-/,'#fieldset-');
    	}
        var fsInput = jqForm.find('input[name="fieldset.current"]');
        if (selected && fsInput) {
            fsInput.val(selected);
        }
    });

    $("#archetypes-schemata-links").addClass('hiddenStructure');
    $("div.formControls input[name='form.button.previous']," +
      "div.formControls input[name='form.button.next']").remove();

};

$.fn.ploneTabInit = function(pbo) {
    return this.each(function() {
        var item = $(this);

        item.find("form.enableFormTabbing,div.enableFormTabbing").each(ploneFormTabbing.initializeForm);
        item.find("dl.enableFormTabbing").each(ploneFormTabbing.initializeDL);

        //Select tab if it's part of the URL or designated in a hidden input
        var targetPane = item.find('.enableFormTabbing input[name="fieldset.current"]').val() || window.location.hash;
        if (targetPane) {
            item.find(".enableFormTabbing .formTab a[href='" +
             targetPane.replace("'", "").replace(/^#fieldset-/, "#fieldsetlegend-") +
             "']").click();
        }
    });
};

// initialize is a convenience function
ploneFormTabbing.initialize = function() {
    $('body').ploneTabInit();
};

})(jQuery);

jQuery(function(){ploneFormTabbing.initialize();});
