// Tooltip-like help pop-ups used in forms
// XXX DEPRECATED
var ie=0 
if (navigator.appVersion.indexOf("MSIE")!=-1) { 
  ie=1; 
} 

// Tooltip-like help pop-ups used in forms 
  function formtooltip(el,flag){ 
    elem = document.getElementById(el); 
    if (flag) {  
      if (ie) { 
        elem.parentNode.parentNode.style.zIndex=1000; 
        elem.parentNode.parentNode.style.borderRight='0px solid #000'; 
        // ugly , yes .. but neccesary to avoid a small but very annoying bug in IE6 
      } 
      elem.style.visibility='visible'; 
    } 
    else { 
      if (ie) { 
        elem.parentNode.parentNode.style.zIndex=1; 
        elem.parentNode.parentNode.style.border='none'; 
      } 
      elem.style.visibility='hidden' }; 
  }
