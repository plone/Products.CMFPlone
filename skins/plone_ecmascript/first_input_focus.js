// Focus on error 
function setFocus(){
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    var xre = new RegExp(/\berror\b/);
    // Search only forms to avoid spending time on regular text
    for (var f = 0; (formnode = document.getElementsByTagName('form').item(f)); f++){
        // Search for errors first, focus on first error if found
        for (var i = 0; (node = formnode.getElementsByTagName('div').item(i)); i++) {
            if (xre.exec(node.className)){
                for (var j = 0; (inputnode = node.getElementsByTagName('input').item(j)); j++) {
                    try {
                        if (inputnode.focus) { // check availability first
                            inputnode.focus();
                            return;
                        }
                    } catch(e) {
                        // try next one, this can happen with a hidden or
                        // invisible input field
                    }
                }
            }
        }
        // If no error, focus on input element with tabindex 1
        
        // Update: This code should be re-enabled and tested in Plone 3! We now have ondomload, 
        // which makes it feasible to use this behavior again.
        
        // uncomment to reactivate
        // this part works as intended, but there are too many places where this function causes pain, 
        // moving focus away from a field in which the user is already typing
        
        //for (var i = 0; (node = formnode.getElementsByTagName('input').item(i)); i++) {
         //   if (node.getAttribute('tabindex') == 1) {
         //       node.focus();
         //        return;   
         //   }
        //}

    }
}
registerPloneFunction(setFocus)
