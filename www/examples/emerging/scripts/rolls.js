/* Function that displays status bar messages. */
function MM_displayStatusMsg(msgStr)  { //v3.0
	status=msgStr; document.MM_returnValue = true;
}

function MM_findObj(n, d) { //v3.0
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document); return x;
}
/* Functions that swaps images. */
function MM_swapImage() { //v3.0
  var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
   if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}
function MM_swapImgRestore() { //v3.0
  var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}

/* Functions that handle preload. */
function MM_preloadImages() { //v3.0
 var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
   var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
   if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}

function MM_showHideLayers() { //v3.0
  var i,p,v,obj,args=MM_showHideLayers.arguments;
  for (i=0; i<(args.length-2); i+=3) if ((obj=MM_findObj(args[i]))!=null) { v=args[i+2];
    if (obj.style) { obj=obj.style; v=(v=='show')?'visible':(v='hide')?'hidden':v; }
    obj.visibility=v; }
}

function MM_openBrWindow(theURL,winName,features) { //v2.0
  window.open(theURL,winName,features);
}




var mousex = 0;
var mousey = 0;
names = new Array('about','careers','approach','clients','partners','news');


// This is the timer ...
function CheckLoaded() {
  for (l=0; l<names.length; l++) {
     if (document.all) {
         if (!document.all[names[l]]) {
             return false;
         }
     } else {
         if (!document.layers[names[l]]) {
             return false;
         }
     }
  }
return true; 
}

function LayerClean() {
  
  // Get the mouse x,y coors -- 
  //   if outsite image layers -- Hide all of them
  //   if on coor boundry then show layer ahnd hide all.

  x = 0;
  y = 0;
  xx = 0;
  yy = 0;
  inRegion = -1;
  
  if (document.all && CheckLoaded()) {
    for (l=0; l < names.length; l++) {
     x = parseInt(document.all[names[l]].style.left);
     y = parseInt(document.all[names[l]].style.top);
     xx = x + parseInt(document.all[names[l]].style.width);
     yy = y + parseInt(document.all[names[l]].style.height) + 35;
     if (mousex > x && mousex < xx && mousey > y && mousey < yy) {
        inRegion = l;
        for(u=0; u < names.length; u++) {
           if (u != l) 
              document.all[names[u]].style.visibility = "hidden";
        }
     }
    }
    if (inRegion == -1 && mousey > 140)
MM_showHideLayers('careers','','hide','news','','hide','about','','hide','approach','','hide','clients','','hide','partners','','hide');
  } else {
    if (CheckLoaded()) {
    for (l=0; l <= names.length; l++) {
     x = parseInt(document.layers[names[l]].left);
     y = parseInt(document.layers[names[l]].top);
     xx = x + parseInt(document.layers[names[l]].width);
     yy = y + parseInt(document.layers[names[l]].height) + 35;
     if (mousex > x && mousex < xx && mousey > y && mousey < yy) {
        inRegion = l;
        for(u=0; u < names.length; u++) {
           if (u != l) 
              document.layers[names[u]].visibility = "hidden";
        }
     }
     }
    }
    if (inRegion == -1 && mousey > 140)
MM_showHideLayers('careers','','hide','news','','hide','about','','hide','approach','','hide','clients','','hide','partners','','hide');
  }
}

// Silly Mouse coord catcher

function mouseMoveHandler (evt) {
  mousex = document.all ? event.clientX : document.layers ? evt.x : 
evt.clientX;
  mousey = document.all ? event.clientY : document.layers ? evt.y : 
evt.clientY;
//  window.status = "x " + mousex + ": y " + mousey;
  LayerClean();
}


if (document.layers)
  document.captureEvents(Event.MOUSEMOVE);
if (document.layers || document.all)
  document.onmousemove = mouseMoveHandler;
if (document.addEventListener)
  document.addEventListener('mousemove', mouseMoveHandler, true);



