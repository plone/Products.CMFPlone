// Functions for selecting all checkboxes in folder_contents/search_form view
function selectAll(id, formName) {
    // Get the elements. if formName is provided, get the elements inside the form
    if (formName==null) {
        checkboxes = document.getElementsByName(id)
        for (i = 0; i < checkboxes.length; i++){
            checkboxes[i].checked = true ;
            }
    } else {
        for (i=0; i<document.forms[formName].elements.length;i++){
            if (document.forms[formName].elements[i].name==id){
                document.forms[formName].elements[i].checked=true; 
                }
            }
        }
    }
function deselectAll(id, formName) {
    if (formName==null) {
        checkboxes = document.getElementsByName(id)
        for (i = 0; i < checkboxes.length; i++){
            checkboxes[i].checked = false ;}
    } else {
        for (i=0; i<document.forms[formName].elements.length;i++){
            if (document.forms[formName].elements[i].name==id){
                document.forms[formName].elements[i].checked=false;
                }
            }
        }
    }
function toggleSelect(selectbutton, id, initialState, formName) {
    /* required selectbutton: you can pass any object that will function as a toggle
     * optional id: id of the the group of checkboxes that needs to be toggled (default=ids:list
     * optional initialState: initial state of the group. (default=false)
     * e.g. folder_contents is false, search_form=true because the item boxes
     * are checked initially.
     * optional formName: name of the form in which the boxes reside, use this if there are more
     * forms on the page with boxes with the same name
     */
    id=id || 'ids:list'  // defaults to ids:list, this is the most common usage

    if (selectbutton.isSelected==null){
        initialState=initialState || false;
        selectbutton.isSelected=initialState;
        }
    /* create and use a property on the button itself so you don't have to 
     * use a global variable and we can have as much groups on a page as we like.
     */
    if (selectbutton.isSelected == false) {
        selectbutton.setAttribute('src', portal_url + '/select_none_icon.gif');
        selectbutton.isSelected=true;
        return selectAll(id, formName);
    } else {
        selectbutton.setAttribute('src',portal_url + '/select_all_icon.gif');
        selectbutton.isSelected=false;
        return deselectAll(id, formName);
        }
    } 
