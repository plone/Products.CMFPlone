// Focus on error 
function setFocus(){
    var xre = new RegExp(/\berror\b/);
    // Search only forms to avoid spending time on regular text
    for (var f = 0; (formnode = document.getElementsByTagName('form').item(f)); f++){
        // Search for errors first, focus on first error if found
        for (var i = 0; (node = formnode.getElementsByTagName('div').item(i)); i++) {
            if (xre.exec(node.className)){
                for (var j = 0; (inputnode = node.getElementsByTagName('input').item(j)); j++) {
                    inputnode.focus();
                    return;   
                }
            }
        }
    }
}
registerPloneFunction(setFocus)
