/* Essential javascripts, used a lot. 
 * These should be placed inline
 * We have to be certain they are loaded before anything that uses them 
 */
function registerPloneFunction(func){
    // registers a function to fire onload.     
    if (window.addEventListener) window.addEventListener("load",func,false);
    else if (window.attachEvent) window.attachEvent("onload",func);   
}
function unRegisterPloneFunction(func){
    // uregisters a function so it does not fire onload anyway 
    if (window.removeEventListener) window.removeEventListener("load",func,false);
    else if (window.detachEvent) window.detachEvent("onload",func);   
}
function getContentArea(){
    node =  document.getElementById('region-content')
    if (! node){
        node = document.getElementById('content')
        }
    return node
} 