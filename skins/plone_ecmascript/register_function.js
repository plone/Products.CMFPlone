/* Essential javascripts, used a lot. 
 * These should be placed inline
 * We have to be certain they are loaded before anything that uses them 
 */

function registerEventListener(elem, event, func) {
    if (elem.addEventListener) elem.addEventListener(event, func, false);
    else if (elem.attachEvent) elem.attachEvent("on"+event, func);
}

function unRegisterEventListener(elem, event, func) {
    if (elem.removeEventListener) elem.removeEventListener(event, func, false);
    else if (elem.detachEvent) elem.detachEvent("on"+event, func);
}

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
