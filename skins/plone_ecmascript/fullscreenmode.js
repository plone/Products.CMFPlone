
function setDisplayMode(item, state) {
// change the display prop of a div to none/block if the div exists
    if (document.getElementById(item) != null) {
        document.getElementById(item).style.display = state;
    }
}
function fullscreenMode() {
    // toggle the display prop of divs none/block    
	if (document.getElementById('portal-top').style.display == 'none') {        
	    setDisplayMode('portal-top', 'block');
        setDisplayMode('portal-column-one', 'table-cell');
        setDisplayMode('portal-column-two', 'table-cell');
        // set cookie        
	    createCookie('fullscreenMode', '');        
	}    else {    
	    setDisplayMode('portal-top', 'none');
        setDisplayMode('portal-column-one', 'none');
        setDisplayMode('portal-column-two', 'none');        
	    createCookie('fullscreenMode', '1');    
	}
}

function fullscreenModeLoad() {
// based on cookie hide div
    	if (readCookie('fullscreenMode') == '1') {        
	    setDisplayMode('portal-top', 'none');
        setDisplayMode('portal-column-one', 'none');
        setDisplayMode('portal-column-two', 'none');    
	}
}

registerPloneFunction(fullscreenModeLoad)
