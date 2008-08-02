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

var ploneFormTabbing = {};

ploneFormTabbing._toggleFactory = function(container, tab_ids, panel_ids) {
    return function(e) {
        jq(tab_ids).removeClass('selected');
        jq(panel_ids).addClass('hidden');

        var orig_id = this.tagName.toLowerCase() == 'a' ? 
            '#' + this.id : jq(this).val();
        var id = orig_id.replace(/^#fieldsetlegend-/, "#fieldset-");
        jq(orig_id).addClass('selected');
        jq(id).removeClass('hidden');

        jq(container).find("input[name=fieldset.current]").val(orig_id);
        return false;
    }
};

ploneFormTabbing._buildTabs = function(container, legends) {
    var threshold = 6;
    var tab_ids = [];
    var panel_ids = [];

    legends.each(function(i) {
        tab_ids[i] = '#' + this.id;
        panel_ids[i] = tab_ids[i].replace(/^#fieldsetlegend-/, "#fieldset-");
    });
    var handler = ploneFormTabbing._toggleFactory(
        container, tab_ids.join(','), panel_ids.join(','));

    if (legends.length > threshold) {
        var tabs = document.createElement("select");
        var tabtype = 'option';
        jq(tabs).change(handler).addClass('noUnloadProtection');
    } else {
        var tabs = document.createElement("ul");
        var tabtype = 'li';
    }
    jq(tabs).addClass('formTabs');

    legends.each(function() {
        var tab = document.createElement(tabtype);
        jq(tab).addClass('formTab');

        if (legends.length > threshold) {
            jq(tab).text(jq(this).text());
            tab.id = this.id;
            tab.value = '#' + this.id;
        } else {
            var a = document.createElement("a");
            a.id = this.id;
            a.href = "#" + this.id;
            jq(a).click(handler);
            var span = document.createElement("span");
            jq(span).text(jq(this).text());
            a.appendChild(span);
            tab.appendChild(a);
        }
        tabs.appendChild(tab);
        jq(this).remove();
    });
    
    jq(tabs).children(':first').addClass('firstFormTab');
    jq(tabs).children(':last').addClass('lastFormTab');
    
    return tabs;
};

ploneFormTabbing.select = function($which) {
    if (typeof $which == "string")
        $which = jq($which.replace(/^#fieldset-/, "#fieldsetlegend-"));

    if ($which[0].tagName.toLowerCase() == 'a') {
        $which.click();
        return true;
    } else if ($which[0].tagName.toLowerCase() == 'option') {
        $which.attr('selected', true);
        $which.parent().change();
        return true;
    } else {
        $which.change();
        return true;
    }
    return false;
};

ploneFormTabbing.initializeDL = function() {
    var tabs = jq(ploneFormTabbing._buildTabs(this, jq(this).children('dt')));
    jq(this).before(tabs);
    jq(this).children('dd').addClass('formPanel');

    tabs = tabs.find('li.formTab a,option.formTab');
    if (tabs.length)
        ploneFormTabbing.select(tabs.filter(':first'));
};

ploneFormTabbing.initializeForm = function() {
    var fieldsets = jq(this).children('fieldset');
    
    if (!fieldsets.length) return;
    
    var tabs = ploneFormTabbing._buildTabs(
        this, fieldsets.children('legend'));
    jq(this).prepend(tabs);
    fieldsets.addClass("formPanel");
    
    // The fieldset.current hidden may change, but is not content
    jq(this).find('input[name=fieldset.current]').addClass('noUnloadProtection');

    var tab_inited = false;

    jq(this).find('.formPanel:has(div.field.error)').each(function() {
        var id = this.id.replace(/^fieldset-/, "#fieldsetlegend-");
        var tab = jq(id);
        tab.addClass("notify");
        if (tab.length && !tab_inited)
            tab_inited = ploneFormTabbing.select(tab);
    });

    jq(this).find('.formPanel:has(div.field span.fieldRequired)')
        .each(function() {
        var id = this.id.replace(/^fieldset-/, "#fieldsetlegend-");
        jq(id).addClass('required');
    });

    if (!tab_inited) {
        jq('input[name=fieldset.current][value^=#]').each(function() {
            tab_inited = ploneFormTabbing.select(jq(this).val());
        });
    }

    if (!tab_inited) {
        var tabs = jq("form.enableFormTabbing li.formTab a,"+
                     "form.enableFormTabbing option.formTab,"+
                     "div.enableFormTabbing li.formTab a,"+
                     "div.enableFormTabbing option.formTab");
        if (tabs.length)
            ploneFormTabbing.select(tabs.filter(':first'));
    }

    jq("#archetypes-schemata-links").addClass('hiddenStructure');
    jq("div.formControls input[name=form_previous]," +
      "div.formControls input[name=form_next]").remove();
};

jq(function() {
    jq("form.enableFormTabbing,div.enableFormTabbing")
        .each(ploneFormTabbing.initializeForm);
    jq("dl.enableFormTabbing").each(ploneFormTabbing.initializeDL);
});
