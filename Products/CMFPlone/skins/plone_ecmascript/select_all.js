// Functions for selecting all/none checkboxes in folder_contents/search_form view

/*
  Provides global toggleSelect; see search_form.pt for example usage.
*/

/*global portal_url */

function toggleSelect(selectbutton, id, initialState, formName) {
    /* required selectbutton: you can pass any object that will function as a toggle
     * optional id: id of the the group of checkboxes that needs to be toggled (default=ids:list
     * optional initialState: initial state of the group. (default=false)
     * e.g. folder_contents is false, search_form=true because the item boxes
     * are checked initially.
     * optional formName: name of the form in which the boxes reside, use this if there are more
     * forms on the page with boxes with the same name
     */

    /* If this browser is an IE8 or older AND this event handler has been registered on a
     * change event AND this IS a change event, do nothing.
     * Change events are broken in IE <= 8:
     * http://www.quirksmode.org/dom/events/change.html
     * jQuery tries to fix this:
     * http://api.jquery.com/change/
     * jquery creates simulated change event handlers which arrive here as click events.
     * (Interesting side note, this can result in change and click event handlers
     *  for the same object to be triggered in different orders, depending on the browser)
     * As such, we can ignore the change events, also because they get triggered when they
     * shouldn't, like, when clicking on some random thing AFTER clicking on a select all
     * checkbox.
     */
    if (/MSIE [5-8]\./.test(navigator.userAgent) && event.type === "change" && /toggleSelect\(/.test(selectbutton.onchange.toString())){
        return;
    }
    var fid, state, base;

    fid = id || 'ids:list';  // defaults to ids:list, this is the most common usage
    state = selectbutton.isSelected;
    if (state === undefined) {
        state = Boolean(initialState);
    }

    // create and use a property on the button itself so you don't have to 
    // use a global variable and we can have as much groups on a page as we like.
    selectbutton.isSelected = !state;
    jQuery(selectbutton).attr('src', portal_url+'/select_'+(state?'all':'none')+'_icon.png');
    base = formName ? jQuery(document.forms[formName]) : jQuery(document);
    base.find('input[name="' + fid + '"]:checkbox').prop('checked', !state);
}
