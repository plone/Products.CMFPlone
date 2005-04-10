
function setDisplayMode(item, state) {
// change the display prop of a div to none/block if the div exists
    if (document.getElementById(item) != null) {
        document.getElementById(item).style.display = state;
    }
}
function fullscreenMode() {
    // toggle the display prop of divs none/block    
    // XXX FIXME : this one needs fixing before 2.1 final
    // IE cannot handle dinsplay:table-cell properly
    // Mozilla shifts margins if we do display:block
    // - We need a browser-capabilties-branching here
    if (document.getElementById('portal-column-one').style.display == 'none') {        
        //setDisplayMode('portal-top', 'block');
        setDisplayMode('portal-column-one', 'table-cell');
        setDisplayMode('portal-column-two', 'table-cell');
        if(!document.getElementById('portal-column-one').style.display){
            // silly IE does not understand display:table-cell, so we must workaround
            setDisplayMode('portal-column-one', 'block');
            setDisplayMode('portal-column-two', 'block');
        }
        // set cookie        
        createCookie('fullscreenMode', '');        
    }else {    
        //setDisplayMode('portal-top', 'none');
        setDisplayMode('portal-column-one', 'none');
        setDisplayMode('portal-column-two', 'none');        
        createCookie('fullscreenMode', '1');    
    }
}

function fullscreenModeLoad() {
// based on cookie hide div
    	if (readCookie('fullscreenMode') == '1') {        
	    //setDisplayMode('portal-top', 'none');
        setDisplayMode('portal-column-one', 'none');
        setDisplayMode('portal-column-two', 'none');    
	}
}
registerPloneFunction(fullscreenModeLoad)