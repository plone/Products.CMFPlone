// Essential javascripts, used a lot. even though it may seem painful, these must be place inline, to make sure they are loaded first.

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